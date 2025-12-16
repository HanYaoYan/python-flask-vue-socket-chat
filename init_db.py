"""
数据库初始化脚本
用于创建数据库表结构
"""
from app import app, db
from models import User, Message, Room, RoomMember

def init_database():
    """初始化数据库"""
    with app.app_context():
        print('开始创建数据库表...')
        db.create_all()
        print('数据库表创建成功！')
        print('表列表:')
        print('  - users (用户表)')
        print('  - rooms (房间表)')
        print('  - room_members (房间成员表)')
        print('  - messages (消息表)')

if __name__ == '__main__':
    init_database()

