# 🌐 WEB VERSION - Bảng Thông Tin Công Cộng

## Giới Thiệu

Bảng Thông Tin Công Cộng bây giờ có thể chạy trên **Web Browser**! 
Truy cập từ bất kỳ thiết bị nào trên cùng mạng mà không cần cài đặt thêm phần mềm.

## 🚀 Cách Chạy

### Windows
```bash
# Cách 1: Nhấp đúp vào file
run_web.bat

# Cách 2: Chạy từ PowerShell
python app_web.py
```

### Linux / macOS
```bash
# Cách 1
chmod +x run_web.sh
./run_web.sh

# Cách 2
python3 app_web.py
```

## 📱 Truy Cập

Sau khi chạy server, mở trình duyệt và truy cập:

**Từ máy chạy server:**
```
http://localhost:5000
```

**Từ máy khác trên mạng:**
```
http://<IP_SERVER>:5000
```

Ví dụ: `http://192.168.1.100:5000`

## ⌨️ Điều Khiển

### Nút Bấm (GUI)
- **⬅️ Trang Trước** - Quay lại trang trước
- **Trang Tiếp ➡️** - Tới trang tiếp theo
- **🔍 Phóng To** - Phóng to nội dung
- **🔍 Thu Nhỏ** - Thu nhỏ nội dung
- **⬆️ Cuộn Lên** - Cuộn nội dung lên
- **⬇️ Cuộn Xuống** - Cuộn nội dung xuống
- **🔄 Reset** - Đặt lại view về mặc định

### Phím Tắt (Keyboard)
| Phím | Chức Năng |
|------|-----------|
| `← / →` | Chuyển trang |
| `↑ / ↓` | Cuộn nội dung |
| `+ / -` | Phóng to / Thu nhỏ |
| `R` | Đặt lại view |

## 🔌 API Endpoints

### GET `/`
Trang chính (HTML)

### GET `/api/render`
Lấy khung hình hiện tại dưới dạng JPEG (Base64)

**Response:**
```json
{
  "success": true,
  "image": "data:image/jpeg;base64,...",
  "current_page": 1,
  "total_pages": 5,
  "zoom_level": "1.0x"
}
```

### GET `/api/info`
Lấy thông tin hệ thống

**Response:**
```json
{
  "total_pages": 5,
  "current_page": 1,
  "zoom_level": "1.0x",
  "width": 1280,
  "height": 720
}
```

### POST `/api/action/<action>`
Thực hiện hành động

**Actions:**
- `next_page` - Trang tiếp
- `prev_page` - Trang trước
- `zoom_in` - Phóng to
- `zoom_out` - Thu nhỏ
- `scroll_up` - Cuộn lên
- `scroll_down` - Cuộn xuống
- `reset` - Đặt lại

**Response:**
```json
{
  "success": true,
  "current_page": 2,
  "total_pages": 5,
  "zoom_level": "1.0x"
}
```

## 📋 Yêu Cầu

- Python 3.8 hoặc mới hơn
- Flask 2.0+ (cài đặt tự động)
- OpenCV, MediaPipe, Pillow, NumPy, PyYAML (từ requirements.txt)

## 🔧 Cấu Hình

Chỉnh sửa file `config.yaml` để tùy chỉnh:

```yaml
display:
  width: 1280          # Chiều rộng
  height: 720          # Chiều cao
```

## 📊 Thông Tin Hệ Thống

- **Trang**: Hiển thị trang hiện tại và tổng số trang
- **Zoom**: Mức phóng to/thu nhỏ hiện tại
- **Cập nhật**: Tự động cập nhật khung hình mỗi 500ms

## 🌍 Triển Khai Online

### Sử dụng Ngrok (công khai trên Internet)
```bash
pip install ngrok
python app_web.py &
ngrok http 5000
```

Chia sẻ URL từ Ngrok để người khác truy cập

### Sử dụng VPS/Cloud Server
1. Upload code lên server
2. Cài đặt dependencies: `pip install -r requirements.txt`
3. Chạy với production server (Gunicorn, uWSGI, etc.)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app_web:app
```

## 🐛 Xử Lý Sự Cố

### Port 5000 đã được sử dụng
```bash
# Thay đổi port trong app_web.py
# Tìm dòng: app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)
# Đổi 5000 thành port khác, ví dụ 8000
```

### Không thể truy cập từ máy khác
- Kiểm tra tường lửa cho phép port 5000
- Sử dụng `ipconfig` (Windows) hoặc `ifconfig` (Linux) để tìm IP server
- Thử ping server để kiểm tra kết nối

### Hình ảnh không cập nhật
- Kiểm tra console server có lỗi gì
- Làm mới trang web (`F5`)
- Xóa cache trình duyệt

## 📚 Thêm Thông Tin

- Xem [README.md](README.md) chính cho cài đặt cơ bản
- Xem [QUICKSTART.md](QUICKSTART.md) cho hướng dẫn nhanh
- Xem [GUIDE.md](GUIDE.md) cho hướng dẫn chi tiết

## 📝 Ghi Chú

- Web version không hỗ trợ nhận diện cử chỉ từ camera (sử dụng nút bấm hoặc phím tắt)
- Mỗi lần tải lại trang sẽ reset view về mặc định
- Hỗ trợ nhiều client kết nối đồng thời

## 🎉 Tính Năng

✅ Hiển thị bảng thông tin với giao diện đẹp
✅ Điều khiển qua nút bấm hoặc phím tắt
✅ Cập nhật thời gian thực
✅ Phóng to/thu nhỏ linh hoạt
✅ Cuộn nội dung mượt mà
✅ Hỗ trợ đa ngôn ngữ (Tiếng Việt)
✅ API RESTful cho tích hợp
✅ Giao diện responsive (mobile-friendly)

---

**Tác giả**: Sinh viên
**Phiên bản**: 1.0.0
**Ngày cập nhật**: 2026-05-18
