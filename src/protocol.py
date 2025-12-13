"""
Module định nghĩa giao thức giao tiếp giữa client và server
"""

import json
from datetime import datetime
import struct

# Các hằng số
HEADER_SIZE = 4  # 4 bytes cho chiều dài dữ liệu
ENCODING = 'utf-8'
MAX_PACKET_SIZE = 4096

class Protocol:
    """Lớp xử lý giao thức giao tiếp"""
    
    @staticmethod
    def encode_message(level, message, source):
        """
        Mã hóa thông điệp thành bytes để gửi qua socket
        Format: {"level": "INFO", "message": "...", "source": "...", "timestamp": "..."}
        """
        log_data = {
            "level": level,
            "message": message,
            "source": source,
            "timestamp": datetime.now().isoformat()
        }
        
        json_data = json.dumps(log_data, ensure_ascii=False)
        data_bytes = json_data.encode(ENCODING)
        
        # Thêm header chứa độ dài dữ liệu
        header = struct.pack('!I', len(data_bytes))
        
        return header + data_bytes
    
    @staticmethod
    def decode_message(data):
        """
        Giải mã bytes nhận được thành đối tượng log
        """
        try:
            json_data = data.decode(ENCODING)
            log_data = json.loads(json_data)
            return log_data
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Nếu không phải JSON, trả về dạng plain text
            return {
                "level": "INFO",
                "message": data.decode(ENCODING, errors='ignore'),
                "source": "Unknown",
                "timestamp": datetime.now().isoformat()
            }
    
    @staticmethod
    def receive_message(sock):
        """
        Nhận toàn bộ message từ socket theo giao thức
        """
        # Nhận header (4 bytes chứa độ dài dữ liệu)
        header_data = b''
        while len(header_data) < HEADER_SIZE:
            chunk = sock.recv(HEADER_SIZE - len(header_data))
            if not chunk:
                return None
            header_data += chunk
        
        # Giải mã độ dài dữ liệu
        data_length = struct.unpack('!I', header_data)[0]
        
        # Nhận dữ liệu
        received_data = b''
        while len(received_data) < data_length:
            chunk = sock.recv(min(4096, data_length - len(received_data)))
            if not chunk:
                break
            received_data += chunk
        
        return received_data