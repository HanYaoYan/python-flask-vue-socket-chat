import eventlet
import os
import socket
from datetime import datetime

# 在 monkey_patch 之前解析 MySQL 和 Redis 主机名为 IP 地址
# 这样可以避免 eventlet greendns 模块的 DNS 解析问题
def resolve_host_to_ip(host, port=None):
    """解析主机名为 IP 地址"""
    if not host:
        return host
    # 如果已经是 IP 地址格式，直接返回
    try:
        parts = host.split('.')
        if len(parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in parts):
            return host
    except:
        pass
    # 尝试解析主机名
    try:
        ip = socket.gethostbyname(host)
        print(f'Resolved {host} to {ip}')
        return ip
    except Exception as e:
        print(f'Warning: Could not resolve {host} to IP: {e}, using hostname directly')
        return host

# 加载配置并解析主机名（在 monkey_patch 之前）
from config import SETTINGS
_mysql_host_original = SETTINGS['database']['mysql']['host']
_redis_host_original = SETTINGS['redis']['host']
_mysql_host_ip = resolve_host_to_ip(_mysql_host_original)
_redis_host_ip = resolve_host_to_ip(_redis_host_original)

# 将解析后的 IP 设置到环境变量，供 Redis 客户端使用
os.environ['REDIS_HOST_IP'] = _redis_host_ip

# 现在进行 monkey_patch
eventlet.monkey_patch()

from flask import Flask
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
from models import db
from models.user import User
from models.message import Message
from models.room import Room, RoomMember
from utils.redis_client import redis_client
import json

# 初始化 Flask 应用
app = Flask(__name__)
app.config['SECRET_KEY'] = SETTINGS['app']['secret_key']

# 配置数据库，使用预先解析的 IP 地址
mysql_config = SETTINGS['database']['mysql']
mysql_host = _mysql_host_ip
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{mysql_config['user']}:{mysql_config['password']}"
    f"@{mysql_host}:{mysql_config['port']}/{mysql_config['database']}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化扩展
db.init_app(app)
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
sio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# 注册蓝图
from routes.auth import auth_bp
from routes.rooms import rooms_bp
from routes.users import users_bp

app.register_blueprint(auth_bp)
app.register_blueprint(rooms_bp)
app.register_blueprint(users_bp)

# Socket.IO 连接的客户端信息 {socket_id: user_id}
connected_users = {}


@sio.on('connect')
def handle_connect(auth):
    """客户端连接"""
    try:
        # 从认证信息或查询参数获取 token
        token = auth.get('token') if isinstance(auth, dict) else None
        if not token:
            token = request.args.get('token')

        if not token:
            print('连接失败: 未提供 token')
            return False

        user = User.verify_token(token)
        if not user:
            print(f'连接失败: token 无效')
            return False

        # 保存连接信息
        connected_users[request.sid] = user.id
        redis_client.set_user_online(user.id, request.sid)

        print(f'用户 {user.username} (ID: {user.id}) 已连接, socket_id: {request.sid}')

        # 广播在线状态更新
        sio.emit('user_online', {'user_id': user.id, 'username': user.username}, broadcast=True)

        return True

    except Exception as e:
        print(f'连接错误: {str(e)}')
        return False


@sio.on('disconnect')
def handle_disconnect():
    """客户端断开连接"""
    try:
        user_id = connected_users.pop(request.sid, None)
        if user_id:
            redis_client.set_user_offline(user_id)
            user = User.query.get(user_id)
            if user:
                print(f'用户 {user.username} (ID: {user_id}) 已断开连接')
                # 广播离线状态更新
                sio.emit('user_offline', {'user_id': user_id}, broadcast=True)
    except Exception as e:
        print(f'断开连接错误: {str(e)}')


@sio.on('join_room')
def handle_join_room(data):
    """加入房间"""
    try:
        user_id = connected_users.get(request.sid)
        if not user_id:
            emit('error', {'message': '未认证'})
            return

        room_id = data.get('room_id')
        if not room_id:
            emit('error', {'message': '房间ID不能为空'})
            return

        # 检查用户是否是房间成员
        if not RoomMember.query.filter_by(room_id=room_id, user_id=user_id).first():
            emit('error', {'message': '不是房间成员'})
            return

        join_room(str(room_id))
        print(f'用户 {user_id} 加入房间 {room_id}')
        emit('joined_room', {'room_id': room_id})

    except Exception as e:
        emit('error', {'message': f'加入房间失败: {str(e)}'})


@sio.on('leave_room')
def handle_leave_room(data):
    """离开房间"""
    try:
        user_id = connected_users.get(request.sid)
        if not user_id:
            return

        room_id = data.get('room_id')
        if room_id:
            leave_room(str(room_id))
            print(f'用户 {user_id} 离开房间 {room_id}')
            emit('left_room', {'room_id': room_id})

    except Exception as e:
        print(f'离开房间错误: {str(e)}')


@sio.on('send_message')
def handle_send_message(data):
    """发送消息"""
    try:
        user_id = connected_users.get(request.sid)
        if not user_id:
            emit('error', {'message': '未认证'})
            return

        user = User.query.get(user_id)
        if not user:
            emit('error', {'message': '用户不存在'})
            return

        content = data.get('content', '').strip()
        room_id = data.get('room_id')
        receiver_id = data.get('receiver_id')

        if not content:
            emit('error', {'message': '消息内容不能为空'})
            return

        # 验证：必须有房间ID或接收者ID
        if not room_id and not receiver_id:
            emit('error', {'message': '必须指定房间或接收者'})
            return

        # 如果是群聊，检查用户是否是房间成员
        if room_id:
            if not RoomMember.query.filter_by(room_id=room_id, user_id=user_id).first():
                emit('error', {'message': '不是房间成员'})
                return

        # 创建消息记录
        message = Message(
            sender_id=user_id,
            room_id=room_id,
            receiver_id=receiver_id,
            content=content
        )
        db.session.add(message)
        db.session.commit()

        # 先写 MySQL 后更 Redis（数据一致性原则）
        message_dict = message.to_dict()

        # 缓存到 Redis
        if room_id:
            redis_client.cache_message(room_id, json.dumps(message_dict, default=str))

        # 准备发送的消息数据
        emit_data = {
            'message': message_dict,
            'timestamp': datetime.utcnow().isoformat()
        }

        # 发送消息
        if room_id:
            # 群聊：发送给房间内的所有用户
            sio.emit('new_message', emit_data, room=str(room_id))
        else:
            # 单聊：发送给发送者和接收者
            sender_socket = redis_client.get_user_socket_id(user_id)
            receiver_socket = redis_client.get_user_socket_id(receiver_id)

            if sender_socket:
                sio.emit('new_message', emit_data, room=sender_socket)
            if receiver_socket:
                sio.emit('new_message', emit_data, room=receiver_socket)

        print(f'用户 {user.username} 发送消息到房间 {room_id or f"用户 {receiver_id}"}')

    except Exception as e:
        db.session.rollback()
        print(f'发送消息错误: {str(e)}')
        emit('error', {'message': f'发送消息失败: {str(e)}'})


@app.route('/')
def index():
    """主页"""
    return {'message': 'Chat API Server', 'version': '1.0.0'}


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    try:
        # 测试数据库连接
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        db_status = 'connected'
    except:
        db_status = 'disconnected'

    try:
        # 测试 Redis 连接
        redis_client.ping()
        redis_status = 'connected'
    except:
        redis_status = 'disconnected'

    return {
        'status': 'ok',
        'database': db_status,
        'redis': redis_status
    }


def init_db():
    """初始化数据库"""
    import time
    import sys
    from sqlalchemy import text
    max_retries = 30
    retry_delay = 2

    print('开始初始化数据库...')
    for attempt in range(max_retries):
        try:
            with app.app_context():
                db.create_all()
                print('数据库表创建成功')
                return
        except Exception as e:
            if attempt < max_retries - 1:
                print(f'数据库连接失败，{retry_delay}秒后重试... ({attempt + 1}/{max_retries})')
                print(f'错误信息: {str(e)[:100]}')
                sys.stdout.flush()
                time.sleep(retry_delay)
            else:
                print(f'数据库初始化失败，已重试{max_retries}次: {str(e)}')
                sys.stdout.flush()
                raise


if __name__ == '__main__':
    # 初始化数据库
    init_db()

    # 运行应用
    host = SETTINGS['app']['host']
    port = SETTINGS['app']['port']
    debug = SETTINGS['app']['debug']

    print(f'服务器启动: http://{host}:{port}')
    sio.run(app, host=host, port=port, debug=debug)
