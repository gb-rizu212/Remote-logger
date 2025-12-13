"""
Module xử lý việc ghi log vào file với cơ chế đồng bộ hóa
"""

import threading
from datetime import datetime
import os

class FileLogger:
    """Lớp quản lý việc ghi log vào file với thread-safe"""
    
    def __init__(self, log_file="logs/log.txt", max_size_mb=10):
        """
        Khởi tạo logger
        
        Args:
            log_file: Đường dẫn file log
            max_size_mb: Kích thước tối đa của file log (MB)
        """
        self.log_file = log_file
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.lock = threading.Lock()
        
        # Tạo thư mục logs nếu chưa tồn tại
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Tạo file log nếu chưa tồn tại
        if not os.path.exists(log_file):
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(f"=== Log File Created at {datetime.now().isoformat()} ===\n\n")
    
    def write_log(self, level, message, source, timestamp=None):
        """
        Ghi log vào file với timestamp
        
        Args:
            level: Mức độ log (INFO, WARNING, ERROR)
            message: Nội dung log
            source: Nguồn gửi log
            timestamp: Thời gian (nếu None sẽ dùng thời gian hiện tại)
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        # Định dạng dòng log
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            time_str = timestamp
        
        log_line = f"[{time_str}] [{source}] [{level}]: {message}\n"
        
        # Đồng bộ hóa việc ghi file
        with self.lock:
            # Kiểm tra kích thước file
            if os.path.exists(self.log_file):
                file_size = os.path.getsize(self.log_file)
                if file_size > self.max_size_bytes:
                    self._rotate_log()
            
            # Ghi log vào file
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_line)
    
    def _rotate_log(self):
        """Xoay file log khi đạt kích thước tối đa"""
        backup_file = f"{self.log_file}.backup"
        
        # Đổi tên file hiện tại thành backup
        if os.path.exists(backup_file):
            os.remove(backup_file)
        
        os.rename(self.log_file, backup_file)
        
        # Tạo file log mới
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write(f"=== Log File Rotated at {datetime.now().isoformat()} ===\n\n")
    
    def read_recent_logs(self, num_lines=100):
        """
        Đọc các dòng log gần đây nhất
        
        Args:
            num_lines: Số dòng cần đọc
        Returns:
            List các dòng log
        """
        if not os.path.exists(self.log_file):
            return []
        
        with open(self.log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        return lines[-num_lines:] if len(lines) > num_lines else lines