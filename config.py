import os
from dotenv import load_dotenv

load_dotenv()

SETTINGS = {
    'app': {
        'schema': os.environ.get('SCHEMA', 'http://'),
        'host': os.environ.get('HOST', '0.0.0.0'),
        'port': int(os.environ.get('PORT', 9000)),
        'debug': os.environ.get('DEBUG', 'False').lower() == 'true',
        'secret_key': os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
    },
    'database': {
        'mysql': {
            'host': os.environ.get('MYSQL_HOST', 'localhost'),
            'port': int(os.environ.get('MYSQL_PORT', 3306)),
            'user': os.environ.get('MYSQL_USER', 'root'),
            'password': os.environ.get('MYSQL_PASSWORD', 'password'),
            'database': os.environ.get('MYSQL_DATABASE', 'chat_db')
        }
    },
    'redis': {
        'host': os.environ.get('REDIS_HOST', 'localhost'),
        'port': int(os.environ.get('REDIS_PORT', 6379)),
        'db': int(os.environ.get('REDIS_DB', 0)),
        'password': os.environ.get('REDIS_PASSWORD', None),
        'decode_responses': True
    },
    'jwt': {
        'secret_key': os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production'),
        'algorithm': 'HS256',
        'expiration': 86400  # 24小时
    }
}
