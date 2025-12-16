from flask import Blueprint, request, jsonify
from models.user import User
from utils.redis_client import redis_client

users_bp = Blueprint('users', __name__, url_prefix='/api/users')


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
        
        # 搜索用户名或邮箱
        users = User.query.filter(
            (User.username.like(f'%{keyword}%')) | (User.email.like(f'%{keyword}%'))
        ).limit(20).all()
        
        return jsonify({
            'users': [u.to_dict() for u in users]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'搜索用户失败: {str(e)}'}), 500

