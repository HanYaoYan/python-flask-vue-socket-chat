import redis
import os


class RedisClient:
    _instance = None
    _redis_client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisClient, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._redis_client is None:
            # 从环境变量获取 Redis 配置，支持 IP 地址
            redis_host = os.environ.get('REDIS_HOST_IP') or os.environ.get('REDIS_HOST', 'localhost')
            redis_port = int(os.environ.get('REDIS_PORT', 6379))

            # redis_db 表示 Redis 使用哪个“逻辑数据库”编号（是0~15的整数）
            # Redis 本身支持多个逻辑数据库（通常为16个，编号从0到15），相当于同一个 Redis 实例下划分的多个“独立单元”，
            # 每个编号下存储的数据互不干扰，相当于 MySQL 里的“某个库”（database），而不是“表（table）”。
            # 比如你可以在 Redis 的 db=0 存缓存，db=1 存session等，但现实中生产实践往往只用 db=0。
            # 注意，MySQL 是通过数据库名字区分“库”，而不是编号。而 Redis 的逻辑数据库通过编号区分。
            redis_db = int(os.environ.get('REDIS_DB', 0))
            redis_password = os.environ.get('REDIS_PASSWORD', None)
            # 创建 Redis 客户端实例（使用上面获取的端口和密码）
            self._redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                password=redis_password,
                decode_responses=True
            )

    # 简单概括：@property 用于把方法变为属性，可用 obj.client 而不是 obj.client() 调用，更简洁。
    @property
    def client(self):
        """获取 Redis 客户端实例"""
        return self._redis_client

    # =========================
    # 在线状态 / socket 映射
    # =========================
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

    # =========================
    # 群聊消息缓存
    # =========================
    # 缓存最新消息到 Redis（最多缓存 limit 条消息）
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

    # =========================
    # 私聊消息缓存
    # =========================
    @staticmethod
    def _private_key(user_a_id, user_b_id):
        """生成私聊缓存 key，按用户 ID 排序保证双方一致"""
        a, b = sorted([int(user_a_id), int(user_b_id)])
        return f"private:{a}:{b}:messages"

    def cache_private_message(self, user_a_id, user_b_id, message_data, limit=100):
        """缓存最新私聊消息"""
        key = self._private_key(user_a_id, user_b_id)
        import json
        if isinstance(message_data, dict):
            message_data = json.dumps(message_data, default=str)
        self._redis_client.lpush(key, message_data)
        self._redis_client.ltrim(key, 0, limit - 1)
        # 私聊缓存 24 小时
        self._redis_client.expire(key, 86400)

    def get_private_messages(self, user_a_id, user_b_id, count=100):
        """获取最新私聊消息（倒序，调用方可反转）"""
        key = self._private_key(user_a_id, user_b_id)
        return self._redis_client.lrange(key, 0, count - 1)

    def clear_private_cache(self, user_a_id, user_b_id):
        """清除私聊缓存"""
        key = self._private_key(user_a_id, user_b_id)
        self._redis_client.delete(key)


# 全局 Redis 客户端实例，单例模式
# 之所以是"单例模式”，是因为 redis_client = RedisClient() 只在本文件执行一次，
# 其他模块都是直接 from utils.redis_client import redis_client，
# 这样无论在哪里 import，获取的都是这个已经创建好的 redis_client 实例——不会重复创建新实例。
redis_client = RedisClient()

