from flask import Blueprint, request, jsonify
from models import db
from models.user import User
from models.room import Room, RoomMember
from models.message import Message
from utils.redis_client import redis_client
import json

rooms_bp = Blueprint('rooms', __name__, url_prefix='/api/rooms')


def get_current_user(request):
    """从请求头获取当前用户"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return None
    return User.verify_token(token)


@rooms_bp.route('/', methods=['GET'])
def get_rooms():
    """获取用户所在的房间列表"""
    try:
        user = get_current_user(request)
        if not user:
            return jsonify({'error': '未认证'}), 401
        
        # 获取用户所在的房间
        room_members = RoomMember.query.filter_by(user_id=user.id).all()
        rooms = [member.room for member in room_members]
        
        return jsonify({
            'rooms': [room.to_dict() for room in rooms]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取房间列表失败: {str(e)}'}), 500


@rooms_bp.route('/', methods=['POST'])
def create_room():
    """创建房间"""
    try:
        user = get_current_user(request)
        if not user:
            return jsonify({'error': '未认证'}), 401
        
        data = request.get_json()
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        room_type = data.get('room_type', 'group')
        
        if not name:
            return jsonify({'error': '房间名称不能为空'}), 400
        
        # 创建房间
        room = Room(
            name=name,
            description=description,
            room_type=room_type,
            created_by=user.id
        )
        db.session.add(room)
        db.session.flush()  # 获取 room.id
        
        # 添加创建者为管理员
        member = RoomMember(room_id=room.id, user_id=user.id, role='admin')
        db.session.add(member)
        db.session.commit()
        
        return jsonify({
            'message': '房间创建成功',
            'room': room.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'创建房间失败: {str(e)}'}), 500


@rooms_bp.route('/<int:room_id>/join', methods=['POST'])
def join_room(room_id):
    """加入房间"""
    try:
        user = get_current_user(request)
        if not user:
            return jsonify({'error': '未认证'}), 401
        
        room = Room.query.get_or_404(room_id)
        
        # 检查是否已经是成员
        if RoomMember.query.filter_by(room_id=room_id, user_id=user.id).first():
            return jsonify({'error': '已经是房间成员'}), 400
        
        # 添加成员
        member = RoomMember(room_id=room_id, user_id=user.id)
        db.session.add(member)
        db.session.commit()
        
        return jsonify({
            'message': '加入房间成功',
            'room': room.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'加入房间失败: {str(e)}'}), 500


@rooms_bp.route('/<int:room_id>/messages', methods=['GET'])
def get_messages(room_id):
    """获取房间消息（分页）"""
    try:
        user = get_current_user(request)
        if not user:
            return jsonify({'error': '未认证'}), 401
        
        # 检查用户是否是房间成员
        if not RoomMember.query.filter_by(room_id=room_id, user_id=user.id).first():
            return jsonify({'error': '不是房间成员'}), 403
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        # 先从 Redis 缓存获取最新消息
        cached_messages = redis_client.get_cached_messages(room_id, per_page)
        
        if cached_messages and page == 1:
            # 第一页优先使用缓存
            messages = [json.loads(msg) for msg in cached_messages]
        else:
            # 从数据库查询
            pagination = Message.query.filter_by(room_id=room_id)\
                .order_by(Message.created_at.desc())\
                .paginate(page=page, per_page=per_page, error_out=False)
            
            messages = [msg.to_dict() for msg in pagination.items]
            messages.reverse()  # 按时间正序
        
        return jsonify({
            'messages': messages,
            'page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取消息失败: {str(e)}'}), 500

