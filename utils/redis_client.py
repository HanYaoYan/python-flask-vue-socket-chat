import redis
from config import SETTINGS


class RedisClient:
    _instance = None
    _redis_client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisClient, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._redis_client is None:
            redis_config = SETTINGS['redis']
            self._redis_client = redis.Redis(
                host=redis_config['host'],
                port=redis_config['port'],
                db=redis_config['db'],
                password=redis_config.get('password'),
                decode_responses=redis_config.get('decode_responses', True)
            )
    
    @property
    def client(self):
        """获取 Redis 客户端实例"""
        return self._redis_client
    
    def set_user_online(self, user_id, socket_id):
        """设置用户在线状态"""
        key = f"user:{user_id}:online"
        self._redis_client.setex(key, 300, socket_id)  # 5分钟过期
        self._redis_client.sadd("online_users", user_id)
    
    def set_user_offline(self, user_id):
        """设置用户离线状态"""
        key = f"user:{user_id}:online"
        self._redis_client.delete(key)
        self._redis_client.srem("online_users", user_id)
    
    def is_user_online(self, user_id):
        """检查用户是否在线"""
        key = f"user:{user_id}:online"
        return self._redis_client.exists(key) > 0
    
    def get_user_socket_id(self, user_id):
        """获取用户的 socket_id"""
        key = f"user:{user_id}:online"
        return self._redis_client.get(key)
    
    def get_online_users(self):
        """获取所有在线用户ID列表"""
        return [int(uid) for uid in self._redis_client.smembers("online_users")]
    
    def cache_message(self, room_id, message_data, limit=50):
        """缓存最新消息到 Redis"""
        key = f"room:{room_id}:messages"
        # 使用列表存储，保留最新的 limit 条消息
        import json
        if isinstance(message_data, dict):
            message_data = json.dumps(message_data, default=str)
        self._redis_client.lpush(key, message_data)
        self._redis_client.ltrim(key, 0, limit - 1)
        self._redis_client.expire(key, 3600)  # 1小时过期
    
    def get_cached_messages(self, room_id, count=50):
        """从 Redis 获取缓存的消息"""
        key = f"room:{room_id}:messages"
        messages = self._redis_client.lrange(key, 0, count - 1)
        return messages
    
    def clear_room_cache(self, room_id):
        """清除房间消息缓存"""
        key = f"room:{room_id}:messages"
        self._redis_client.delete(key)


# 全局 Redis 客户端实例
redis_client = RedisClient().client

