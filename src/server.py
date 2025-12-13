"""
Máy chủ nhận log từ các client và ghi vào file
"""

import socket
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import queue
from datetime import datetime
import sys
import os

# Thêm thư mục src vào path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.protocol import Protocol
from src.logger import FileLogger

class RemoteLoggerServer:
    """Lớp quản lý máy chủ ghi log từ xa"""
    
    def __init__(self, host='0.0.0.0', port=9999):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        self.clients = []
        self.client_threads = []
        self.log_queue = queue.Queue()
        
        # Khởi tạo logger
        self.logger = FileLogger()
        
        # Tạo giao diện
        self.setup_gui()
        
    def setup_gui(self):
        """Thiết lập giao diện người dùng"""
        self.root = tk.Tk()
        self.root.title("Remote Logger Server")
        self.root.geometry("900x700")
        
        # Cấu hình grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Frame chính
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Tiêu đề
        title_label = ttk.Label(main_frame, text="📊 HỆ THỐNG GHI LOG TỪ XA - SERVER", 
                                font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 15))
        
        # Panel thông tin server
        info_frame = ttk.LabelFrame(main_frame, text="Thông tin Server", padding="10")
        info_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Hiển thị IP
        ttk.Label(info_frame, text="Địa chỉ IP:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.ip_label = ttk.Label(info_frame, text=self.get_local_ip(), font=("Arial", 10, "bold"))
        self.ip_label.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        # Hiển thị Port
        ttk.Label(info_frame, text="Port:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.port_label = ttk.Label(info_frame, text=str(self.port), font=("Arial", 10, "bold"))
        self.port_label.grid(row=0, column=3, sticky=tk.W, padx=(0, 20))
        
        # Trạng thái
        ttk.Label(info_frame, text="Trạng thái:").grid(row=0, column=4, sticky=tk.W, padx=(0, 5))
        self.status_label = ttk.Label(info_frame, text="⏸️ Dừng", foreground="red", 
                                     font=("Arial", 10, "bold"))
        self.status_label.grid(row=0, column=5, sticky=tk.W)
        
        # Panel điều khiển
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, columnspan=2, pady=(0, 15))
        
        # Nút điều khiển
        self.start_btn = ttk.Button(control_frame, text="▶️ Khởi động Server", 
                                   command=self.start_server, width=20)
        self.start_btn.grid(row=0, column=0, padx=5)
        
        self.stop_btn = ttk.Button(control_frame, text="⏹️ Dừng Server", 
                                  command=self.stop_server, state=tk.DISABLED, width=20)
        self.stop_btn.grid(row=0, column=1, padx=5)
        
        # Panel hiển thị log
        log_frame = ttk.LabelFrame(main_frame, text="Log nhận được", padding="10")
        log_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Tạo text area hiển thị log
        self.log_display = scrolledtext.ScrolledText(log_frame, height=20, font=("Consolas", 10))
        self.log_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Cấu hình màu cho các loại log
        self.log_display.tag_config("INFO", foreground="black")
        self.log_display.tag_config("WARNING", foreground="orange")
        self.log_display.tag_config("ERROR", foreground="red")
        self.log_display.tag_config("SYSTEM", foreground="blue", font=("Consolas", 10, "bold"))
        
        # Panel thống kê
        stats_frame = ttk.Frame(main_frame)
        stats_frame.grid(row=4, column=0, columnspan=2, pady=(15, 0))
        
        # Thống kê client
        ttk.Label(stats_frame, text="👥 Clients:").grid(row=0, column=0, padx=(0, 5))
        self.client_count_label = ttk.Label(stats_frame, text="0", font=("Arial", 10, "bold"))
        self.client_count_label.grid(row=0, column=1, padx=(0, 20))
        
        # Thống kê log
        ttk.Label(stats_frame, text="📝 Logs:").grid(row=0, column=2, padx=(0, 5))
        self.log_count_label = ttk.Label(stats_frame, text="0", font=("Arial", 10, "bold"))
        self.log_count_label.grid(row=0, column=3, padx=(0, 20))
        
        # Nút xem file log
        view_log_btn = ttk.Button(stats_frame, text="📂 Mở File Log", 
                                 command=self.open_log_file, width=15)
        view_log_btn.grid(row=0, column=4, padx=20)
        
        # Biến thống kê
        self.total_logs = 0
        
        # Bắt đầu xử lý queue
        self.process_queue()
        
    def get_local_ip(self):
        """Lấy địa chỉ IP cục bộ"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def start_server(self):
        """Khởi động server"""
        if self.running:
            return
        
        try:
            # Tạo socket server
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            
            self.running = True
            self.status_label.config(text="▶️ Đang chạy", foreground="green")
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            
            # Khởi động thread lắng nghe kết nối
            server_thread = threading.Thread(target=self.accept_connections, daemon=True)
            server_thread.start()
            
            self.add_system_log(f"Server đã khởi động trên {self.host}:{self.port}")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể khởi động server: {str(e)}")
    
    def stop_server(self):
        """Dừng server"""
        if not self.running:
            return
        
        self.running = False
        
        # Đóng kết nối với tất cả client
        for client in self.clients:
            try:
                client.close()
            except:
                pass
        self.clients.clear()
        
        # Đóng socket server
        if self.server_socket:
            self.server_socket.close()
        
        # Cập nhật giao diện
        self.status_label.config(text="⏸️ Dừng", foreground="red")
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.client_count_label.config(text="0")
        
        self.add_system_log("Server đã dừng")
    
    def accept_connections(self):
        """Chấp nhận kết nối từ client"""
        while self.running:
            try:
                client_socket, client_address = self.server_socket.accept()
                self.clients.append(client_socket)
                
                # Cập nhật số client
                self.root.after(0, self.update_client_count)
                
                # Tạo thread xử lý client
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_address),
                    daemon=True
                )
                client_thread.start()
                self.client_threads.append(client_thread)
                
                self.add_system_log(f"Client kết nối từ {client_address[0]}:{client_address[1]}")
                
            except Exception as e:
                if self.running:
                    self.add_system_log(f"Lỗi khi chấp nhận kết nối: {str(e)}")
                break
    
    def handle_client(self, client_socket, client_address):
        """Xử lý kết nối từ client"""
        client_ip = client_address[0]
        
        while self.running:
            try:
                # Nhận message theo giao thức
                data = Protocol.receive_message(client_socket)
                if not data:
                    break
                
                # Giải mã message
                log_data = Protocol.decode_message(data)
                
                # Ghi log vào file
                self.logger.write_log(
                    log_data.get("level", "INFO"),
                    log_data.get("message", ""),
                    log_data.get("source", client_ip),
                    log_data.get("timestamp")
                )
                
                # Thêm vào queue hiển thị
                self.log_queue.put(log_data)
                
            except ConnectionResetError:
                break
            except Exception as e:
                self.add_system_log(f"Lỗi xử lý client {client_ip}: {str(e)}")
                break
        
        # Đóng kết nối
        self.close_client_connection(client_socket, client_ip)
    
    def close_client_connection(self, client_socket, client_ip):
        """Đóng kết nối client"""
        try:
            client_socket.close()
            if client_socket in self.clients:
                self.clients.remove(client_socket)
            
            # Cập nhật số client
            self.root.after(0, self.update_client_count)
            
            self.add_system_log(f"Client {client_ip} đã ngắt kết nối")
        except:
            pass
    
    def update_client_count(self):
        """Cập nhật số lượng client"""
        count = len(self.clients)
        self.client_count_label.config(text=str(count))
    
    def add_system_log(self, message):
        """Thêm log hệ thống"""
        log_data = {
            "level": "SYSTEM",
            "message": message,
            "source": "SERVER",
            "timestamp": datetime.now().isoformat()
        }
        self.log_queue.put(log_data)
    
    def process_queue(self):
        """Xử lý queue để hiển thị log"""
        try:
            while not self.log_queue.empty():
                log_data = self.log_queue.get_nowait()
                
                level = log_data.get("level", "INFO")
                message = log_data.get("message", "")
                source = log_data.get("source", "Unknown")
                timestamp = log_data.get("timestamp", "")
                
                # Định dạng thời gian
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    time_str = dt.strftime("%H:%M:%S")
                except:
                    time_str = timestamp
                
                # Định dạng dòng log
                formatted_log = f"[{time_str}] [{source}] [{level}]: {message}\n"
                
                # Thêm vào hiển thị
                self.log_display.insert(tk.END, formatted_log, level)
                self.log_display.see(tk.END)
                
                # Cập nhật số log
                if level != "SYSTEM":
                    self.total_logs += 1
                    self.log_count_label.config(text=str(self.total_logs))
                
                # Tự động xóa log cũ
                if self.total_logs > 1000:
                    self.log_display.delete(1.0, 100.0)
                    
        except queue.Empty:
            pass
        
        # Lên lịch xử lý lại
        self.root.after(100, self.process_queue)
    
    def open_log_file(self):
        """Mở file log trong ứng dụng"""
        try:
            with open("logs/log.txt", "r", encoding='utf-8') as f:
                content = f.read()
            
            # Tạo cửa sổ mới để hiển thị file log
            log_window = tk.Toplevel(self.root)
            log_window.title("File Log - logs/log.txt")
            log_window.geometry("800x600")
            
            text_widget = scrolledtext.ScrolledText(log_window, font=("Consolas", 10))
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            text_widget.insert(tk.END, content)
            text_widget.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể đọc file log: {str(e)}")
    
    def run(self):
        """Chạy ứng dụng server"""
        self.root.mainloop()

def main():
    """Hàm main để chạy server"""
    server = RemoteLoggerServer()
    server.run()

if __name__ == "__main__":
    main()