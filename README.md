# HỆ THỐNG BẢNG THÔNG TIN CÔNG CỘNG KHÔNG CHẠM
# Gesture Controlled Public Information Display System

## 📋 Mô tả dự án

Đây là một hệ thống bảng thông tin điều khiển hoàn toàn bằng cử chỉ tay, không cần chạm vào màn hình. Sử dụng công nghệ MediaPipe để nhận diện tay và các cử chỉ được định nghĩa sẵn.

### 🎯 Ứng dụng thực tế
- ✈️ **Sân bay**: Hướng dẫn đường bay, thông tin gate, giờ khởi hành
- 🏬 **Trung tâm thương mại**: Bản đồ, danh sách cửa hàng, khuyến mãi
- 🏥 **Bệnh viện**: Thông tin khoa phòng, lịch khám, hướng dẫn
- 🎓 **Trường học**: Thời khóa biểu, thông báo, lịch sự kiện
- 🚌 **Nhà ga, bến xe**: Giá vé, lịch trình, thông tin tuyến
- 🎬 **Rạp chiếu phim**: Suất chiếu, giá vé, đặt vé
- 🏛️ **Bảo tàng**: Thông tin triển lãm, lịch sử tác phẩm

---

## 🎮 Các cử chỉ được hỗ trợ

| Cử chỉ | Tác dụng | Mô tả |
|--------|---------|-------|
| **Vuốt sang TRÁI** | Chuyển trang tiếp theo | Di chuyển tay từ phải sang trái |
| **Vuốt sang PHẢI** | Chuyển trang trước | Di chuyển tay từ trái sang phải |
| **Cuộn LÊN** | Cuộn nội dung lên | Di chuyển tay từ dưới lên trên |
| **Cuộn XUỐNG** | Cuộn nội dung xuống | Di chuyển tay từ trên xuống dưới |
| **ZOOM IN** | Phóng to | Đưa hai tay lại gần nhau |
| **ZOOM OUT** | Thu nhỏ | Tách hai tay ra xa |
| **NẮM TAY (GRAB)** | Tạm dừng/Lựa chọn | Gập tất cả các ngón tay |

---

## 📁 Cấu trúc thư mục

```
Thành phố thông minh/
├── main.py                 # File chính, chạy ứng dụng
├── gesture.py             # Module nhận diện cử chỉ
├── gui.py                 # Module giao diện hiển thị
├── config.py              # Module quản lý cấu hình
├── data_manager.py        # Module quản lý dữ liệu nội dung
├── config.yaml            # File cấu hình mẫu
├── requirements.txt       # Danh sách thư viện cần cài
├── README.md             # File này
├── data/
│   └── pages.json        # Dữ liệu nội dung (tự động tạo)
└── assets/               # Thư mục ảnh/file đính kèm
```

---

## 🔧 Cài đặt & Chạy

### 1. Cài đặt Python (yêu cầu Python 3.8+)
```bash
# Kiểm tra phiên bản Python
python --version
```

### 2. Cài đặt thư viện cần thiết
```bash
pip install -r requirements.txt
```

### 3. Tạo dữ liệu mẫu
```bash
python -c "from data_manager import DataManager; dm = DataManager(); dm.create_sample_data()"
```

### 4. Chạy ứng dụng
```bash
python main.py
```

**Hoặc với cấu hình tùy chỉnh:**
```bash
python main.py --config config.yaml --camera 0
```

---

## ⌨️ Phím tắt trong ứng dụng

| Phím | Chức năng |
|------|----------|
| **D** | Bật/Tắt chế độ Debug |
| **P** | Tạm dừng/Tiếp tục |
| **R** | Reset view (zoom = 1x, scroll = 0) |
| **N** | Chuyển trang tiếp theo |
| **B** | Chuyển trang trước |
| **Q** hoặc **ESC** | Thoát chương trình |

---

## 📝 Cấu trúc file dữ liệu (data/pages.json)

```json
[
  {
    "title": "Tiêu đề trang",
    "content": "Nội dung text của trang, hỗ trợ ký tự Unicode",
    "images": null
  },
  {
    "title": "Trang có hình ảnh",
    "content": "Nội dung kèm hình ảnh",
    "images": ["path/to/image.png"]
  }
]
```

---

## 🔧 Cấu hình (config.yaml)

Bạn có thể tùy chỉnh các thông số sau:

```yaml
# Độ phân giải màn hình
display_width: 1280
display_height: 720

# Độ phân giải camera
camera_width: 640
camera_height: 480
camera_fps: 30

# Độ tin cậy phát hiện (0.0 - 1.0)
# Giá trị cao hơn = chính xác hơn nhưng chậm hơn
min_detection_confidence: 0.5
min_tracking_confidence: 0.5

# Ngưỡng phát hiện cử chỉ (pixels)
swipe_threshold: 50
zoom_threshold: 20
scroll_threshold: 30
```

---

## 📊 Module & Chức năng

### gesture.py - Nhận diện cử chỉ
- **GestureType**: Enum các loại cử chỉ
- **GestureFrame**: Chứa dữ liệu khung hình + cử chỉ
- **GestureRecognizer**: Xử lý video stream và nhận diện cử chỉ
  - `process_frame()`: Xử lý một khung hình
  - `detect_swipe()`: Phát hiện vuốt
  - `detect_zoom()`: Phát hiện zoom
  - `is_fist()`: Kiểm tra nắm tay

### gui.py - Giao diện hiển thị
- **ContentType**: Loại nội dung (TEXT, IMAGE, MIXED)
- **Page**: Lưu trữ một trang nội dung
- **DisplayGUI**: Render giao diện bảng thông tin
  - `next_page()`: Trang tiếp theo
  - `previous_page()`: Trang trước
  - `zoom_in()` / `zoom_out()`: Phóng to/thu nhỏ
  - `scroll_up()` / `scroll_down()`: Cuộn nội dung
  - `render()`: Render khung hình

### config.py - Quản lý cấu hình
- **Config**: Dataclass chứa tất cả cấu hình
  - `load()`: Tải từ file YAML/JSON
  - `save()`: Lưu vào file

### data_manager.py - Quản lý dữ liệu
- **DataManager**: Quản lý nội dung trang
  - `load_pages()`: Tải từ file JSON
  - `save_pages()`: Lưu vào file JSON
  - `create_sample_data()`: Tạo dữ liệu mẫu

### main.py - Ứng dụng chính
- **GestureControlledDisplay**: Lớp chính, tích hợp tất cả
  - `run()`: Vòng lặp chính
  - `handle_gesture()`: Xử lý cử chỉ
  - `process_keyboard()`: Xử lý bàn phím

---

## 🐛 Khắc phục sự cố

### Lỗi: "Camera not found"
```bash
# Kiểm tra camera
# Windows:
ls COM*  # Hoặc kiểm tra Device Manager

# Thử camera khác
python main.py --camera 1
```

### Lỗi: "ModuleNotFoundError: No module named 'mediapipe'"
```bash
pip install mediapipe opencv-python numpy pyyaml
```

### Nhận diện cử chỉ không chính xác
1. Tăng `min_detection_confidence` trong `config.yaml` (0.5 → 0.7)
2. Đảm bảo ánh sáng đủ
3. Giảm `swipe_threshold` để nhạy hơn

### Hiệu suất chậm
1. Giảm độ phân giải camera: `camera_width: 320`, `camera_height: 240`
2. Tăng `min_tracking_confidence` lên 0.7-0.8
3. Giảm FPS: `camera_fps: 15`

---

## 💡 Mở rộng & Tùy chỉnh

### Thêm cử chỉ mới
Sửa file `gesture.py`, thêm vào `GestureType` enum:
```python
class GestureType(Enum):
    NEW_GESTURE = "new_gesture"
```

Rồi thêm hàm phát hiện trong `GestureRecognizer`:
```python
def detect_new_gesture(self, ...):
    # Logic phát hiện
    return GestureType.NEW_GESTURE
```

### Thêm trang nội dung mới
```python
from gui import Page
from data_manager import DataManager

dm = DataManager()
page = Page(title="Trang mới", content="Nội dung...")
dm.add_page(page)
```

### Thay đổi giao diện
Sửa màu sắc trong `gui.py`:
```python
self.bg_color = (25, 25, 112)      # Thay đổi màu nền
self.text_color = (255, 255, 255)  # Thay đổi màu text
self.title_color = (0, 255, 255)   # Thay đổi màu tiêu đề
```

---

## 📈 Thống kê & Logging

Chương trình tự động ghi lại:
- Tổng số khung hình xử lý
- Số lần nhận diện từng loại cử chỉ
- Thời gian chạy

In ra console khi thoát ứng dụng.

---

## 📚 Thư viện sử dụng

| Thư viện | Phiên bản | Mục đích |
|---------|----------|---------|
| OpenCV | 4.8.1 | Xử lý video/ảnh |
| MediaPipe | 0.10.9 | Nhận diện tay/gesture |
| NumPy | 1.24.3 | Tính toán số học |
| PyYAML | 6.0.1 | Đọc file cấu hình |

---

## 🎓 Kiến thức cần có

- **Python**: Cơ bản về OOP, dataclass, enum
- **OpenCV**: Xử lý ảnh, vẽ hình học
- **MediaPipe**: Hand tracking, landmarks
- **YAML/JSON**: Định dạng dữ liệu

---

## 📄 License

Dự án này được tạo cho mục đích học tập.

---

## 👨‍💼 Tác giả

**Sinh viên** - Hệ thống Thành phố thông minh

---

## 🤝 Đóng góp

Để cải thiện dự án:
1. Fork dự án
2. Tạo branch mới (`git checkout -b feature/AmazingFeature`)
3. Commit thay đổi (`git commit -m 'Add some AmazingFeature'`)
4. Push lên branch (`git push origin feature/AmazingFeature`)
5. Mở Pull Request

---

## ❓ Câu hỏi thường gặp (FAQ)

**Q: Tôi có thể sử dụng với nhiều camera không?**
A: Có, sửa `camera_id` trong config hoặc dùng flag `--camera 1`

**Q: Có thể lưu video?**
A: Có thể sửa code để thêm `cv2.VideoWriter` vào `main.py`

**Q: Có tính năng tiếng nói không?**
A: Không, nhưng có thể thêm text-to-speech dùng `pyttsx3` hoặc API

**Q: Làm sao để tối ưu hóa nhận diện?**
A: Xem phần "Khắc phục sự cố" phía trên

---

**Chúc bạn thành công! Good luck! 🚀**
