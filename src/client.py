"""
Máy khách gửi log đến server
"""

import socket
import threading
import tkinter as tk
from tkinter import ttk, messagebox, font
import json
from datetime import datetime

from protocol import Protocol

class RemoteLoggerClient:
    """Lớp quản lý máy khách gửi log"""
    
    def __init__(self, server_host='127.0.0.1', server_port=9999):
        self.server_host = server_host
        self.server_port = server_port
        self.client_socket = None
        self.connected = False
        self.hostname = socket.gethostname()
        
        # Tạo giao diện
        self.setup_gui()
    
    def setup_gui(self):
        """Thiết lập giao diện người dùng"""
        self.root = tk.Tk()
        self.root.title("Remote Logger Client")
        self.root.geometry("700x550")
        
        # Cấu hình grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Frame chính
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Tiêu đề
        title_label = ttk.Label(main_frame, text="📤 CLIENT GỬI LOG", 
                                font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 15))
        
        # Panel kết nối
        conn_frame = ttk.LabelFrame(main_frame, text="Kết nối đến Server", padding="10")
        conn_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Nhập địa chỉ server
        ttk.Label(conn_frame, text="IP Server:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.server_ip_entry = ttk.Entry(conn_frame, width=20)
        self.server_ip_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 15))
        self.server_ip_entry.insert(0, self.server_host)
        
        ttk.Label(conn_frame, text="Port:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.server_port_entry = ttk.Entry(conn_frame, width=10)
        self.server_port_entry.grid(row=0, column=3, sticky=tk.W, padx=(0, 15))
        self.server_port_entry.insert(0, str(self.server_port))
        
        # Nút kết nối
        self.connect_btn = ttk.Button(conn_frame, text="🔗 Kết nối", 
                                     command=self.connect_to_server, width=15)
        self.connect_btn.grid(row=0, column=4, padx=(10, 5))
        
        # Trạng thái kết nối
        self.status_label = ttk.Label(conn_frame, text="❌ Chưa kết nối", 
                                     foreground="red", font=("Arial", 10))
        self.status_label.grid(row=0, column=5, padx=5)
        
        # Panel tạo log
        log_frame = ttk.LabelFrame(main_frame, text="Tạo Log Mới", padding="10")
        log_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        log_frame.columnconfigure(1, weight=1)
        
        # Chọn mức độ log
        ttk.Label(log_frame, text="Mức độ:").grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        self.log_level = tk.StringVar(value="INFO")
        level_combo = ttk.Combobox(log_frame, textvariable=self.log_level,
                                  values=["INFO", "WARNING", "ERROR", "DEBUG"], 
                                  width=12, state="readonly")
        level_combo.grid(row=0, column=1, sticky=tk.W, pady=(0, 10), padx=(5, 15))
        
        # Nhập nguồn log
        ttk.Label(log_frame, text="Nguồn:").grid(row=0, column=2, sticky=tk.W, pady=(0, 10))
        self.source_entry = ttk.Entry(log_frame, width=20)
        self.source_entry.grid(row=0, column=3, sticky=tk.W, pady=(0, 10))
        self.source_entry.insert(0, self.hostname)
        
        # Ô nhập nội dung log
        ttk.Label(log_frame, text="Nội dung:").grid(row=1, column=0, sticky=tk.NW, pady=(0, 5))
        
        self.log_text = tk.Text(log_frame, height=8, width=60, font=("Arial", 10))
        self.log_text.grid(row=1, column=1, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Nút gửi log
        self.send_btn = ttk.Button(log_frame, text="📨 Gửi Log", 
                                  command=self.send_log, state=tk.DISABLED, width=15)
        self.send_btn.grid(row=2, column=0, columnspan=4, pady=(5, 0))
        
        # Panel log đã gửi
        sent_frame = ttk.LabelFrame(main_frame, text="Log Đã Gửi", padding="10")
        sent_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        sent_frame.columnconfigure(0, weight=1)
        sent_frame.rowconfigure(0, weight=1)
        
        # Tạo treeview hiển thị log đã gửi
        columns = ("Thời gian", "Mức độ", "Nội dung")
        self.log_tree = ttk.Treeview(sent_frame, columns=columns, show="headings", height=8)
        
        # Định nghĩa cột
        self.log_tree.heading("Thời gian", text="Thời gian")
        self.log_tree.heading("Mức độ", text="Mức độ")
        self.log_tree.heading("Nội dung", text="Nội dung")
        
        self.log_tree.column("Thời gian", width=100)
        self.log_tree.column("Mức độ", width=80)
        self.log_tree.column("Nội dung", width=300)
        
        # Thanh cuộn
        scrollbar = ttk.Scrollbar(sent_frame, orient=tk.VERTICAL, command=self.log_tree.yview)
        self.log_tree.configure(yscrollcommand=scrollbar.set)
        
        # Đặt vị trí
        self.log_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Panel thống kê
        stats_frame = ttk.Frame(main_frame)
        stats_frame.grid(row=4, column=0, columnspan=2, pady=(15, 0))
        
        # Hiển thị số log đã gửi
        ttk.Label(stats_frame, text="📤 Đã gửi:").grid(row=0, column=0, padx=(0, 5))
        self.sent_count_label = ttk.Label(stats_frame, text="0 log", font=("Arial", 10, "bold"))
        self.sent_count_label.grid(row=0, column=1, padx=(0, 20))
        
        # Nút xóa log đã gửi
        clear_btn = ttk.Button(stats_frame, text="🗑️ Xóa Lịch sử", 
                              command=self.clear_sent_logs, width=15)
        clear_btn.grid(row=0, column=2, padx=10)
        
        # Nút kết nối lại
        self.reconnect_btn = ttk.Button(stats_frame, text="🔄 Kết nối lại", 
                                       command=self.reconnect, state=tk.DISABLED, width=15)
        self.reconnect_btn.grid(row=0, column=3, padx=10)
        
        # Biến thống kê
        self.sent_logs_count = 0
        
        # Gắn sự kiện
        self.log_text.bind("<Control-Return>", lambda e: self.send_log())
        
    def connect_to_server(self):
        """Kết nối đến server"""
        if self.connected:
            return
        
        try:
            self.server_host = self.server_ip_entry.get()
            self.server_port = int(self.server_port_entry.get())
            
            # Tạo socket
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.settimeout(3)
            
            # Kết nối đến server
            self.client_socket.connect((self.server_host, self.server_port))
            self.client_socket.settimeout(None)
            
            self.connected = True
            self.status_label.config(text="✅ Đã kết nối", foreground="green")
            self.connect_btn.config(state=tk.DISABLED)
            self.send_btn.config(state=tk.NORMAL)
            self.reconnect_btn.config(state=tk.NORMAL)
            
            # Khởi động thread lắng nghe
            receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
            receive_thread.start()
            
            self.show_message("Thành công", f"Đã kết nối đến {self.server_host}:{self.server_port}")
            
        except Exception as e:
            self.show_message("Lỗi", f"Không thể kết nối: {str(e)}")
            self.disconnect()
    
    def disconnect(self):
        """Ngắt kết nối từ server"""
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
        
        self.connected = False
        self.client_socket = None
        self.status_label.config(text="❌ Mất kết nối", foreground="red")
        self.connect_btn.config(state=tk.NORMAL)
        self.send_btn.config(state=tk.DISABLED)
    
    def reconnect(self):
        """Kết nối lại đến server"""
        self.disconnect()
        self.connect_to_server()
    
    def send_log(self):
        """Gửi log đến server"""
        if not self.connected:
            self.show_message("Cảnh báo", "Chưa kết nối đến server!")
            return
        
        log_message = self.log_text.get("1.0", tk.END).strip()
        if not log_message:
            self.show_message("Cảnh báo", "Vui lòng nhập nội dung log!")
            return
        
        try:
            # Mã hóa message
            encoded_message = Protocol.encode_message(
                self.log_level.get(),
                log_message,
                self.source_entry.get()
            )
            
            # Gửi đến server
            self.client_socket.sendall(encoded_message)
            
            # Thêm vào treeview
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.log_tree.insert("", 0, values=(timestamp, self.log_level.get(), log_message[:50] + "..."))
            
            # Cập nhật số log đã gửi
            self.sent_logs_count += 1
            self.sent_count_label.config(text=f"{self.sent_logs_count} log")
            
            # Xóa nội dung đã nhập
            self.log_text.delete("1.0", tk.END)
            
        except Exception as e:
            self.show_message("Lỗi", f"Không thể gửi log: {str(e)}")
            self.disconnect()
    
    def receive_messages(self):
        """Nhận phản hồi từ server (nếu có)"""
        while self.connected:
            try:
                # Có thể mở rộng để nhận phản hồi từ server
                data = self.client_socket.recv(1024)
                if not data:
                    break
                
                # Xử lý phản hồi ở đây (nếu cần)
                
            except:
                break
        
        # Mất kết nối
        if self.connected:
            self.root.after(0, self.on_disconnect)
    
    def on_disconnect(self):
        """Xử lý khi mất kết nối"""
        self.disconnect()
        self.show_message("Thông báo", "Đã mất kết nối đến server!")
    
    def clear_sent_logs(self):
        """Xóa lịch sử log đã gửi"""
        for item in self.log_tree.get_children():
            self.log_tree.delete(item)
        
        self.sent_logs_count = 0
        self.sent_count_label.config(text="0 log")
    
    def show_message(self, title, message):
        """Hiển thị messagebox"""
        messagebox.showinfo(title, message)
    
    def run(self):
        """Chạy ứng dụng client"""
        self.root.mainloop()

def main():
    """Hàm main để chạy client"""
    client = RemoteLoggerClient()
    client.run()

if __name__ == "__main__":
    main()