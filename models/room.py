from datetime import datetime
from models import db


class Room(db.Model):
    __tablename__ = 'rooms'

    id = db.Column(db.Integer, primary_key=True)
    room_code = db.Column(db.String(20), unique=True, nullable=False, index=True)  # 随机数字房间ID
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    room_type = db.Column(db.String(20), default='group')  # group, private
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    members = db.relationship('RoomMember', backref='room', lazy='dynamic', cascade='all, delete-orphan')
    creator = db.relationship('User', foreign_keys=[created_by])

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'room_code': self.room_code,
            'name': self.name,
            'description': self.description,
            'room_type': self.room_type,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'member_count': self.members.count()
        }

    def __repr__(self):
        return f'<Room {self.name}>'


class RoomMember(db.Model):
    __tablename__ = 'room_members'

    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.String(20), default='member')  # admin, member

    # 唯一约束：一个用户在一个房间只能有一条记录
    __table_args__ = (db.UniqueConstraint('room_id', 'user_id', name='unique_room_user'),)

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'room_id': self.room_id,
            'user_id': self.user_id,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None,
            'role': self.role
        }

    def __repr__(self):
        return f'<RoomMember room_id={self.room_id} user_id={self.user_id}>'

