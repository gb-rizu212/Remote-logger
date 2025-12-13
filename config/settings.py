"""
Cấu hình hệ thống
"""

import os

# Cấu hình server
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 9999

# Cấu hình client
DEFAULT_SERVER_HOST = '127.0.0.1'
DEFAULT_SERVER_PORT = 9999

# Cấu hình file log
LOG_DIR = 'logs'
LOG_FILE = os.path.join(LOG_DIR, 'log.txt')
MAX_LOG_SIZE_MB = 10  # Kích thước tối đa file log (MB)

# Cấu hình giao thức
BUFFER_SIZE = 4096
ENCODING = 'utf-8'

# Tạo thư mục logs nếu chưa tồn tại
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)