# Hệ thống Ghi Log từ xa (Remote Logger)

## Giới thiệu
Hệ thống ghi log từ xa cho phép các client gửi log đến một server trung tâm để lưu trữ và quản lý. Server nhận log, thêm timestamp và ghi vào file log.txt.

## Thành viên nhóm
- [Tống Thị Thanh Trúc]
- [Lê Hữu Tiến]
- [Lê Nguyễn Ánh Hằng]

## Công nghệ sử dụng
- Python 3.8+
- Socket Programming
- Threading (xử lý đa luồng)
- Tkinter (giao diện đồ họa)
- JSON (định dạng dữ liệu)

## Tính năng chính
### Server
- Nhận kết nối từ nhiều client
- Ghi log vào file với timestamp
- Hiển thị log real-time
- Quản lý kích thước file log
- Thống kê số client và log

### Client
- Kết nối đến server
- Gửi log với các mức độ (INFO, WARNING, ERROR)
- Lưu lịch sử log đã gửi
- Tự động kết nối lại khi mất kết nối

## Cài đặt và chạy

### 1. Clone repository
```bash
git clone <repository-url>
cd remote_logger