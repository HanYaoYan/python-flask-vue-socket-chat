from flask import Blueprint, request, jsonify
from models import db
from models.user import User
from models.friend import Friend
from utils.redis_client import redis_client

users_bp = Blueprint('users', __name__, url_prefix='/api/users')

# 导入 SocketIO 实例（延迟导入避免循环依赖）
def get_socketio():
    from app import get_socketio_instance
    return get_socketio_instance()


def get_current_user(request):
    """从请求头获取当前用户"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return None
    return User.verify_token(token)


@users_bp.route('/online', methods=['GET'])
def get_online_users():
    """获取在线用户列表"""
    try:
        user = get_current_user(request)
        if not user:
            return jsonify({'error': '未认证'}), 401

        online_user_ids = redis_client.get_online_users()
        online_users = []

        for user_id in online_user_ids:
            user_obj = User.query.get(user_id)
            if user_obj:
                online_users.append(user_obj.to_dict())

        return jsonify({
            'online_users': online_users,
            'count': len(online_users)
        }), 200

    except Exception as e:
        return jsonify({'error': f'获取在线用户失败: {str(e)}'}), 500


@users_bp.route('/search', methods=['GET'])
def search_users():
    """搜索用户"""
    try:
        user = get_current_user(request)
        if not user:
            return jsonify({'error': '未认证'}), 401

        keyword = request.args.get('keyword', '').strip()
        if not keyword:
            return jsonify({'error': '搜索关键词不能为空'}), 400

        # 搜索用户名或邮箱，排除自己
        users = User.query.filter(
            User.id != user.id,
            (User.username.like(f'%{keyword}%')) | (User.email.like(f'%{keyword}%'))
        ).limit(20).all()

        return jsonify({
            'users': [u.to_dict() for u in users]
        }), 200

    except Exception as e:
        return jsonify({'error': f'搜索用户失败: {str(e)}'}), 500


@users_bp.route('/friends', methods=['GET'])
def get_friends():
    """获取好友列表"""
    try:
        user = get_current_user(request)
        if not user:
            return jsonify({'error': '未认证'}), 401

        # 获取已接受的好友关系（双向）
        friends = Friend.query.filter(
            ((Friend.user_id == user.id) | (Friend.friend_id == user.id)),
            Friend.status == 'accepted'
        ).all()

        # 转换为好友列表
        friend_list = []
        for friend in friends:
            if friend.user_id == user.id:
                friend_list.append({
                    'id': friend.id,
                    'friend': friend.friend.to_dict() if friend.friend else None
                })
            else:
                friend_list.append({
                    'id': friend.id,
                    'friend': friend.user.to_dict() if friend.user else None
                })

        return jsonify({
            'friends': friend_list
        }), 200

    except Exception as e:
        return jsonify({'error': f'获取好友列表失败: {str(e)}'}), 500


@users_bp.route('/friends/requests', methods=['GET'])
def get_friend_requests():
    """获取好友请求列表（收到的请求）"""
    try:
        user = get_current_user(request)
        if not user:
            return jsonify({'error': '未认证'}), 401

        # 获取发送给当前用户的待处理请求
        requests = Friend.query.filter_by(
            friend_id=user.id,
            status='pending'
        ).all()

        request_list = []
        for req in requests:
            requester = User.query.get(req.user_id)
            if requester:
                request_list.append({
                    'id': req.id,
                    'requester': requester.to_dict(),
                    'created_at': req.created_at.isoformat() if req.created_at else None
                })

        return jsonify({
            'requests': request_list
        }), 200

    except Exception as e:
        return jsonify({'error': f'获取好友请求失败: {str(e)}'}), 500


@users_bp.route('/friends/<int:friend_id>', methods=['POST'])
def add_friend(friend_id):
    """发送好友请求"""
    try:
        user = get_current_user(request)
        if not user:
            return jsonify({'error': '未认证'}), 401

        if friend_id == user.id:
            return jsonify({'error': '不能添加自己为好友'}), 400

        # 检查目标用户是否存在
        target_user = User.query.get(friend_id)
        if not target_user:
            return jsonify({'error': '用户不存在'}), 404

        # 检查是否已经是好友或已有请求
        existing = Friend.query.filter(
            ((Friend.user_id == user.id) & (Friend.friend_id == friend_id)) |
            ((Friend.user_id == friend_id) & (Friend.friend_id == user.id))
        ).first()

        if existing:
            if existing.status == 'accepted':
                return jsonify({'error': '已经是好友'}), 400
            elif existing.status == 'pending':
                if existing.user_id == user.id:
                    return jsonify({'error': '已发送好友请求'}), 400
                else:
                    # 对方已发送请求，直接接受
                    existing.status = 'accepted'
                    db.session.commit()
                    return jsonify({'message': '好友请求已接受'}), 200

        # 创建新的好友请求
        friend_request = Friend(
            user_id=user.id,
            friend_id=friend_id,
            status='pending'
        )
        db.session.add(friend_request)
        db.session.commit()

        return jsonify({
            'message': '好友请求已发送',
            'request': friend_request.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'发送好友请求失败: {str(e)}'}), 500


@users_bp.route('/friends/<int:friend_id>/accept', methods=['POST'])
def accept_friend_request(friend_id):
    """接受好友请求"""
    try:
        user = get_current_user(request)
        if not user:
            return jsonify({'error': '未认证'}), 401

        # 查找发送给当前用户的待处理请求
        friend_request = Friend.query.filter_by(
            user_id=friend_id,
            friend_id=user.id,
            status='pending'
        ).first()

        if not friend_request:
            return jsonify({'error': '好友请求不存在'}), 404

        friend_request.status = 'accepted'
        db.session.commit()

        # 通过 Socket.IO 通知发送请求的用户（用户1）
        try:
            sio = get_socketio()
            sender_socket = redis_client.get_user_socket_id(friend_id)
            if sender_socket:
                sio.emit('friend_request_accepted', {
                    'friend': user.to_dict(),
                    'message': f'{user.username} 已接受您的好友请求'
                }, room=sender_socket)
        except Exception as e:
            # Socket通知失败不影响主流程
            print(f'发送好友接受通知失败: {str(e)}')

        return jsonify({
            'message': '好友请求已接受',
            'friend': friend_request.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'接受好友请求失败: {str(e)}'}), 500


@users_bp.route('/friends/<int:friend_id>', methods=['DELETE'])
def delete_friend(friend_id):
    """删除好友或拒绝好友请求"""
    try:
        user = get_current_user(request)
        if not user:
            return jsonify({'error': '未认证'}), 401

        # 查找好友关系（双向）
        friend_relation = Friend.query.filter(
            ((Friend.user_id == user.id) & (Friend.friend_id == friend_id)) |
            ((Friend.user_id == friend_id) & (Friend.friend_id == user.id))
        ).first()

        if not friend_relation:
            return jsonify({'error': '好友关系不存在'}), 404

        db.session.delete(friend_relation)
        db.session.commit()

        return jsonify({'message': '操作成功'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'操作失败: {str(e)}'}), 500

