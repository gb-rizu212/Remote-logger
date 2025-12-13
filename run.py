#!/usr/bin/env python3
"""
Script chạy hệ thống Remote Logger
"""

import sys
import os
import argparse

# Thêm thư mục src vào path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Hàm main"""
    parser = argparse.ArgumentParser(description='Hệ thống Ghi Log từ xa (Remote Logger)')
    parser.add_argument('mode', choices=['server', 'client'], 
                       help='Chế độ chạy: server hoặc client')
    parser.add_argument('--host', default=None, help='Địa chỉ host')
    parser.add_argument('--port', type=int, default=None, help='Cổng kết nối')
    
    args = parser.parse_args()
    
    if args.mode == 'server':
        from server import RemoteLoggerServer
        host = args.host or '0.0.0.0'
        port = args.port or 9999
        server = RemoteLoggerServer(host, port)
        server.run()
    else:
        from client import RemoteLoggerClient
        host = args.host or '127.0.0.1'
        port = args.port or 9999
        client = RemoteLoggerClient(host, port)
        client.run()

if __name__ == '__main__':
    main()