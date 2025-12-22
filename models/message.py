from datetime import datetime
from models import db


class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=True, index=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), default='text')  # text, system
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # 关系
    room = db.relationship('Room', backref='messages')
    # sender 关系通过 User.sent_messages 的 backref='sender' 自动创建，不需要在这里定义
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'sender': self.sender.to_dict() if self.sender else None,
            'receiver_id': self.receiver_id,
            'room_id': self.room_id,
            'content': self.content,
            'message_type': self.message_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Message {self.id}>'

