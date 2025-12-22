from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .message import Message
from .room import Room, RoomMember
from .friend import Friend

__all__ = ['db', 'User', 'Message', 'Room', 'RoomMember', 'Friend']

