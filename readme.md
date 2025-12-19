# Hệ thống Ghi Log từ xa (Remote Logger)

## Giới thiệu

Hệ thống ghi log từ xa cho phép các client gửi log đến một server trung tâm để lưu trữ và quản lý. Server có nhiệm vụ tiếp nhận log, tự động thêm timestamp và ghi dữ liệu vào file `log.txt`. Hệ thống hỗ trợ nhiều client kết nối đồng thời và phù hợp cho việc giám sát, theo dõi hoạt động của các ứng dụng phân tán.

---

## Thành viên nhóm

* **Tống Thị Thanh Trúc** 
* **Lê Hữu Tiến** 
* **Lê Nguyễn Ánh Hằng** 

---

## Công nghệ sử dụng

* **Python 3.8+** – Ngôn ngữ lập trình chính
* **Socket Programming** – Giao tiếp mạng TCP/IP
* **Threading** – Xử lý đa luồng cho nhiều client
* **Tkinter** – Xây dựng giao diện đồ họa
* **JSON** – Định dạng dữ liệu truyền tải

---

## Cài đặt và chạy

### 1. Clone repository

```bash
git clone https://github.com/your-username/remote-logger.git
cd remote_logger
```

### 2. Cài đặt môi trường 
Bắt buộc cài đặt python vào máy để chạy.


### 3. Chạy ứng dụng

#### Phiên bản GUI

**Chạy Server:**

```bash
python src/server.py
# hoặc
python run.py server --host <địa chỉ ip của server > --port <cổng của server >
```

**Chạy Client:**

```bash
python src/client.py
# hoặc
python run.py client --host <địa chỉ ip của server > --port <cổng của server >
```



##  Tính năng chính

### Server

* Nhận kết nối từ nhiều client đồng thời.
* Ghi log vào file với timestamp tự động.
* Hiển thị log real-time, phân loại màu sắc.
* Thống kê số client và tổng log.
* Giao diện GUI trực quan.

### Client

* Kết nối server qua IP và port.
* Gửi log với mức độ INFO, WARNING, ERROR
* Lưu lịch sử log đã gửi
* Tự động kết nối lại khi mất kết nối
* Hỗ trợ GUI và terminal

---

##  Chạy trên hai máy khác nhau

1. Đảm bảo hai máy cùng mạng và ping được nhau
2. Xác định IP máy server (`ipconfig` hoặc `ifconfig`)
3. Chạy server với IP và port tương ứng
4. Client kết nối đến IP và port của server

---

##  Kiến trúc hệ thống

### Giao thức giao tiếp

```
Client → Server: Plain text hoặc JSON
Server → Client: LOG_RECEIVED
```

### Luồng xử lý

1. Client kết nối server qua TCP socket
2. Client gửi log message
3. Server thêm timestamp
4. Ghi log vào file
5. Gửi phản hồi xác nhận cho client

---

##  Cấu trúc thư mục

```
remote_logger/
├── src/
│   ├── server.py
│   ├── client.py
│   ├── protocol.py
├   ├── logger.py
│   └── logs/
│       └── log.txt
├── config/
│   └── settings.py
├── requirements.txt
├── README.md
└── run.py
```

---

##  Một số lỗi thường gặp

* **Connection refused:** kiểm tra server và firewall
* **Address already in use:** đổi port khác
* **Lỗi encoding:** đảm bảo sử dụng UTF-8

---

##  Hướng phát triển

* Thêm xác thực client
* Lọc log theo mức độ
* Giao diện web
* Tối ưu bằng async/await
* Bảo mật bằng SSL/TLS


---

##  Đánh giá và kết quả

* Hoàn thành MVP
* Hệ thống hoạt động ổn định
* Giao diện dễ sử dụng
* Code có cấu trúc rõ ràng

---

##  License

Dự án được phân phối theo giấy phép MIT. Chỉ sử dụng cho mục đích học tập và nghiên cứu.

---

*Dự án môn Lập trình Mạng – Học kỳ 1, năm 2025 - 2026*
