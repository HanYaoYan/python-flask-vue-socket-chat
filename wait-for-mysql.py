#!/usr/bin/env python3
"""等待MySQL服务就绪的脚本"""
import socket
import time
import sys

def wait_for_mysql(host, port, max_retries=60, delay=1):
    """等待MySQL服务可连接"""
    for i in range(max_retries):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((host, port))
            sock.close()
            if result == 0:
                print(f'MySQL is ready at {host}:{port}')
                return True
        except Exception as e:
            pass
        if i < max_retries - 1:
            print(f'Waiting for MySQL at {host}:{port}... ({i+1}/{max_retries})')
            time.sleep(delay)
    return False

if __name__ == '__main__':
    host = sys.argv[1] if len(sys.argv) > 1 else 'mysql'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 3306

    if wait_for_mysql(host, port):
        sys.exit(0)
    else:
        print(f'MySQL not ready after maximum retries')
        sys.exit(1)

