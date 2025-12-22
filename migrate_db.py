"""
数据库迁移脚本 - 独立运行版本
用于添加 room_code 字段、password_hash 字段和创建 friends 表
"""
import pymysql
import random
from config import SETTINGS

def migrate_database():
    """执行数据库迁移"""
    mysql_config = SETTINGS['database']['mysql']

    print('=' * 50)
    print('开始数据库迁移...')
    print('=' * 50)

    try:
        # 连接数据库
        print(f'\n正在连接数据库: {mysql_config["host"]}:{mysql_config["port"]}/{mysql_config["database"]}')
        conn = pymysql.connect(
            host=mysql_config['host'],
            port=mysql_config['port'],
            user=mysql_config['user'],
            password=mysql_config['password'],
            database=mysql_config['database'],
            charset='utf8mb4'
        )

        cursor = conn.cursor()

        # 1. 检查并添加 room_code 字段
        print('\n[1/3] 检查 rooms 表的 room_code 字段...')
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = %s
            AND TABLE_NAME = 'rooms'
            AND COLUMN_NAME = 'room_code'
        """, (mysql_config['database'],))

        count = cursor.fetchone()[0]

        if count > 0:
            print('  ✓ room_code 字段已存在，跳过')
        else:
            print('  → 正在添加 room_code 字段...')
            # 先添加字段
            cursor.execute("""
                ALTER TABLE rooms
                ADD COLUMN room_code VARCHAR(20) NULL
                AFTER id
            """)

            # 为现有房间生成随机6位数字代码
            print('  → 正在为现有房间生成房间代码...')
            cursor.execute("SELECT id FROM rooms WHERE room_code IS NULL")
            existing_rooms = cursor.fetchall()

            import random
            for room_id in existing_rooms:
                room_code = str(random.randint(100000, 999999))
                # 确保代码唯一
                while True:
                    cursor.execute("SELECT COUNT(*) FROM rooms WHERE room_code = %s", (room_code,))
                    if cursor.fetchone()[0] == 0:
                        break
                    room_code = str(random.randint(100000, 999999))

                cursor.execute("UPDATE rooms SET room_code = %s WHERE id = %s", (room_code, room_id[0]))

            # 设置字段为 NOT NULL 并添加唯一索引
            cursor.execute("""
                ALTER TABLE rooms
                MODIFY COLUMN room_code VARCHAR(20) NOT NULL
            """)
            cursor.execute("""
                CREATE UNIQUE INDEX idx_room_code ON rooms(room_code)
            """)

            conn.commit()
            print('  ✓ 成功添加 room_code 字段并生成房间代码')

        # 2. 检查并添加 password_hash 字段
        print('\n[2/3] 检查 rooms 表的 password_hash 字段...')
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = %s
            AND TABLE_NAME = 'rooms'
            AND COLUMN_NAME = 'password_hash'
        """, (mysql_config['database'],))

        count = cursor.fetchone()[0]

        if count > 0:
            print('  ✓ password_hash 字段已存在，跳过')
        else:
            print('  → 正在添加 password_hash 字段...')
            cursor.execute("""
                ALTER TABLE rooms
                ADD COLUMN password_hash VARCHAR(255) NULL
                AFTER room_type
            """)
            conn.commit()
            print('  ✓ 成功添加 password_hash 字段')

        # 3. 检查并创建 friends 表
        print('\n[3/3] 检查 friends 表...')
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM information_schema.TABLES
            WHERE TABLE_SCHEMA = %s
            AND TABLE_NAME = 'friends'
        """, (mysql_config['database'],))

        count = cursor.fetchone()[0]

        if count > 0:
            print('  ✓ friends 表已存在，跳过')
        else:
            print('  → 正在创建 friends 表...')
            cursor.execute("""
                CREATE TABLE friends (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    friend_id INT NOT NULL,
                    status VARCHAR(20) DEFAULT 'pending',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_user_id (user_id),
                    INDEX idx_friend_id (friend_id),
                    UNIQUE KEY unique_user_friend (user_id, friend_id),
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (friend_id) REFERENCES users(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            conn.commit()
            print('  ✓ 成功创建 friends 表')

        cursor.close()
        conn.close()

        print('\n' + '=' * 50)
        print('✓ 数据库迁移完成！')
        print('=' * 50)
        print('\n现在可以重启后端服务了。')

    except pymysql.Error as e:
        print(f'\n✗ 数据库错误: {str(e)}')
        print('\n请检查：')
        print('  1. 数据库连接配置是否正确（config.py 或 .env 文件）')
        print('  2. 数据库用户是否有 ALTER TABLE 和 CREATE TABLE 权限')
        print('  3. 数据库服务是否正在运行')
        return False
    except Exception as e:
        print(f'\n✗ 迁移失败: {str(e)}')
        return False

    return True

if __name__ == '__main__':
    success = migrate_database()
    exit(0 if success else 1)

