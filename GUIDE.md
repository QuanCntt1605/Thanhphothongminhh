# HƯỚNG DẪN CHI TIẾT CHO GIÁO VIÊN VÀ SINH VIÊN
## Guide for Teachers and Students

---

## 📚 PHẦN 1: GIỚI THIỆU DỰ ÁN

### Mục tiêu học tập
Sinh viên sẽ học được:
- ✅ Xử lý video từ camera với OpenCV
- ✅ Computer vision & nhận diện tay với MediaPipe
- ✅ Thiết kế giao diện GUI với OpenCV
- ✅ Kiến trúc phần mềm modular
- ✅ Quản lý dữ liệu với JSON/YAML
- ✅ Unit testing & debugging
- ✅ Lập trình hướng đối tượng (OOP)

### Kỹ năng ứng dụng
- Computer Vision & AI
- Human-Computer Interaction (HCI)
- Software Architecture
- Data Processing
- Algorithm Design

---

## 📖 PHẦN 2: HƯỚNG DẪN CÁCH DÙNG

### A. Cài đặt lần đầu tiên

#### Bước 1: Chuẩn bị môi trường
```bash
# Mở Command Prompt hoặc PowerShell
# Chuyển đến thư mục dự án
cd "C:\Users\MSI\Downloads\Thành phố thông minh"

# Kiểm tra Python
python --version
# Kết quả: Python 3.8+
```

#### Bước 2: Cài đặt tự động
```bash
# Chạy setup script
python setup.py

# Hoặc cài thủ công
pip install -r requirements.txt
```

#### Bước 3: Chạy test
```bash
python test_modules.py
# Nếu thấy "✅ TẤT CẢ TEST PASSED!" là OK
```

#### Bước 4: Chạy ứng dụng
```bash
python main.py
```

### B. Sử dụng ứng dụng

#### Giao diện
```
┌────────────────────────────────────────────┐
│  TIÊU ĐỀ TRANG (Cyan)                     │
├────────────────────────────────────────────┤
│                                            │
│     NỘI DUNG TEXT/HÌNH ẢNH                │  ┌──────────┐
│     Hỗ trợ zoom & cuộn                    │  │  CAMERA  │
│                                            │  │ PREVIEW  │
│     Dòng tiếp theo...                     │  │          │
│                                            │  └──────────┘
├────────────────────────────────────────────┤
│  Trang 1/3        Zoom: 1.0x               │
└────────────────────────────────────────────┘
```

#### Điều khiển bằng cử chỉ

**1. Chuyển trang**
```
Vuốt SANG PHẢI          Vuốt SANG TRÁI
(Trang trước)           (Trang tiếp theo)
  ←─────────            ─────────→
     Tay                    Tay
```

**2. Cuộn nội dung**
```
Cuộn LÊN                Cuộn XUỐNG
(Di chuyển tay lên)     (Di chuyển tay xuống)
     ↑                        ↓
  ┌─────┐               ┌─────┐
  │ Tay │               │ Tay │
  └─────┘               └─────┘
```

**3. Zoom**
```
Zoom OUT                Zoom IN
(Tách 2 tay ra)        (Đưa 2 tay lại)
  👆       👆           👆       👆
  ├─────────────┤       ├────┤
      [Far]              [Near]
```

**4. Phím bổ sung**
- **D**: Chế độ Debug (hiển thị thông tin)
- **P**: Tạm dừng/Tiếp tục
- **R**: Reset (zoom 1x, scroll 0)
- **N/B**: Trang tiếp theo/trước
- **Q/ESC**: Thoát

#### Thay đổi nội dung

**Cách 1: Sửa trực tiếp trong code**
```python
# Mở main.py, tìm _create_default_content()
page = Page(
    title="Tiêu đề mới",
    content="Nội dung mới của bạn"
)
```

**Cách 2: Tải từ file JSON**
```bash
# Sửa data/pages.json
[
  {
    "title": "Trang 1",
    "content": "Nội dung..."
  }
]
```

**Cách 3: Dùng code**
```python
from data_manager import DataManager
from gui import Page

dm = DataManager()
page = Page(title="Mới", content="Nội dung")
dm.add_page(page)
```

---

## 🔬 PHẦN 3: GIẢI THÍCH KỸ THUẬT

### A. Cấu trúc MediaPipe Hand Detection

```
┌─ Camera Input ──┐
│                 │
│  640x480 RGB    │
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│  MediaPipe Hands    │
│  (TensorFlow Lite)  │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  21 Landmarks/hand  │
│  (3D coordinates)   │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Gesture Detection  │
│  (Vuốt, Zoom, etc)  │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Action Processing  │
│  (Chuyển trang, ..)  │
└─────────────────────┘
```

### B. 21 Landmarks của bàn tay

```
          8 (Ngón trỏ - Index)
          |
    6 ---- 7 ---- 8
    |  
    5
    |
4 - 3 - 2          12 (Ngón giữa)
    |              |
    0              11---12
    | (Cổ tay)     |
    1              10
    
Điểm 0: Cổ tay
Điểm 4,8,12,16,20: Đầu ngón
Các điểm khác: Khớp giữa các ngón
```

**Công thức phát hiện cử chỉ:**
```
Vuốt: So sánh vị trí tay qua nhiều khung hình
  - Nếu (x_end - x_start) > threshold → Vuốt phải
  - Nếu (x_end - x_start) < -threshold → Vuốt trái

Zoom: Tính khoảng cách giữa 2 tay
  - Nếu distance tăng → Zoom Out
  - Nếu distance giảm → Zoom In

Nắm tay: Kiểm tra nếu các ngón đều gập
  - Nếu <2 ngón mở → Grab
```

### C. Workflow xử lý

```
┌──────────────────┐
│  main.py         │
│  (Main Loop)     │
└────────┬─────────┘
         │
         ├─→ capture frame từ camera
         │
         ├─→ gesture.process_frame(frame)
         │   ├─→ convert RGB
         │   ├─→ mediapipe detect hands
         │   ├─→ detect_swipe()
         │   ├─→ detect_zoom()
         │   └─→ return GestureFrame
         │
         ├─→ handle_gesture(gesture)
         │   ├─→ gesture == SWIPE_LEFT?
         │   │   → display.next_page()
         │   ├─→ gesture == ZOOM_IN?
         │   │   → display.zoom_in()
         │   └─→ ...
         │
         ├─→ display.render()
         │   ├─→ tạo nền
         │   ├─→ vẽ tiêu đề
         │   ├─→ vẽ nội dung (áp dụng zoom + scroll)
         │   ├─→ vẽ footer
         │   └─→ return frame
         │
         └─→ imshow(frame)
```

---

## 🔧 PHẦN 4: CẢI TIẾN VÀ MỞ RỘNG

### Bài tập 1: Thêm cử chỉ mới
**Yêu cầu:** Thêm cử chỉ "Vuốt lên" = Quay lại trang chủ

**Hướng dẫn:**
1. Thêm `SWIPE_UP = "swipe_up"` vào `GestureType`
2. Thêm logic phát hiện trong `detect_swipe()`:
```python
if dy < -threshold and abs(dx) < threshold:
    return GestureType.SWIPE_UP
```
3. Thêm xử lý trong `handle_gesture()`:
```python
elif gesture_type == GestureType.SWIPE_UP:
    self.display.current_page = 0
```

### Bài tập 2: Thêm tiếng nói
**Yêu cầu:** Phát tiếng khi chuyển trang

**Hướng dẫn:**
```python
# Cài: pip install pyttsx3

import pyttsx3
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

# Dùng:
speak("Trang tiếp theo")
```

### Bài tập 3: Lưu video
**Yêu cầu:** Ghi lại toàn bộ quá trình

**Hướng dẫn:**
```python
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output.mp4', fourcc, 30.0, (1280, 720))

# Trong vòng lặp:
out.write(info_display)

# Khi thoát:
out.release()
```

### Bài tập 4: Lưu dữ liệu thống kê
**Yêu cầu:** Lưu số lần sử dụng mỗi cử chỉ

**Hướng dẫn:**
```python
# Trong cleanup():
stats = {
    'total_frames': self.frame_count,
    'gestures': self.gesture_count,
    'timestamp': datetime.now().isoformat()
}

with open('stats.json', 'w') as f:
    json.dump(stats, f)
```

### Bài tập 5: Đa ngôn ngữ
**Yêu cầu:** Hỗ trợ Tiếng Anh, Tiếng Nhật

**Hướng dẫn:**
```python
LANGUAGES = {
    'vi': {'next': 'Trang tiếp theo', ...},
    'en': {'next': 'Next page', ...},
    'ja': {'next': '次のページ', ...}
}

current_lang = 'vi'
print(LANGUAGES[current_lang]['next'])
```

---

## 📊 PHẦN 5: HIỆU SUẤT & TỐI ưU

### Đo tốc độ
```python
import time

start = time.time()
# Xử lý
elapsed = time.time() - start

print(f"FPS: {1/elapsed:.1f}")  # Khung/giây
```

### Tối ưu hóa
| Vấn đề | Nguyên nhân | Giải pháp |
|--------|-----------|----------|
| Chậm | Độ phân giải cao | Giảm camera_width, camera_height |
| CPU cao | MediaPipe nặng | Tăng min_detection_confidence |
| Lag | Xử lý hình ảnh | Giảm FPS hoặc độ phân giải |
| Phát hiện sai | Ngưỡng thấp | Tăng swipe_threshold, zoom_threshold |

### Profiling
```python
# Cài: pip install line_profiler

# Dùng @profile trước hàm cần kiểm tra
@profile
def process_frame(self, frame):
    ...

# Chạy: kernprof -l -v main.py
```

---

## 🧪 PHẦN 6: TESTING & QA

### Unit Test
```python
def test_gesture_left_swipe():
    recognizer = GestureRecognizer()
    # Tạo fake landmarks cho vuốt trái
    # ...
    assert gesture == GestureType.SWIPE_LEFT

# Chạy: python -m pytest test_*.py
```

### Integration Test
```python
def test_full_workflow():
    app = GestureControlledDisplay()
    app.load_content()
    assert app.display.get_page_count() > 0
```

### Manual Test Checklist
- [ ] Camera hoạt động
- [ ] Các cử chỉ được nhận diện
- [ ] Chuyển trang mượt
- [ ] Zoom không bị lag
- [ ] Cuộn hoạt động đúng
- [ ] Phím tắt hoạt động
- [ ] Không bị crash

---

## 📝 PHẦN 7: ĐÁNH GIÁ & TIÊU CHÍ

### Tiêu chí điểm (100 điểm)

#### Chức năng cơ bản (40 điểm)
- [ ] (10p) Nhận diện tay chính xác
- [ ] (10p) Nhận diện cử chỉ chính xác
- [ ] (10p) Chuyển trang hoạt động
- [ ] (10p) Zoom & cuộn hoạt động

#### Giao diện & UX (20 điểm)
- [ ] (10p) Giao diện rõ ràng, dễ sử dụng
- [ ] (5p) Có phản hồi trực quan
- [ ] (5p) Không bị flicker/lag

#### Code & Architecture (20 điểm)
- [ ] (10p) Code modular, có comment
- [ ] (5p) Xử lý error tốt
- [ ] (5p) Tối ưu hóa hiệu suất

#### Tài liệu (10 điểm)
- [ ] (5p) README chi tiết
- [ ] (5p) Code có comment

#### Bonus (+10 điểm)
- [ ] (+5p) Thêm cử chỉ mới
- [ ] (+5p) Tích hợp tiếng nói
- [ ] (+5p) Lưu video
- [ ] (+5p) Giao diện đa ngôn ngữ

---

## 🎓 PHẦN 8: TÀI LIỆU THAM KHẢO

### Sách & Khóa học
- **OpenCV Doc**: https://docs.opencv.org/
- **MediaPipe**: https://google.github.io/mediapipe/
- **Python OOP**: Python official docs

### Video hướng dẫn
- OpenCV tutorials (YouTube)
- MediaPipe hand tracking (Official)

### Công cụ hữu ích
- **VS Code** - Editor
- **Git** - Version control
- **Pytest** - Unit testing
- **Line Profiler** - Performance analysis

---

## ❓ PHẦN 9: TROUBLESHOOTING

### Lỗi thường gặp

**Lỗi 1: ModuleNotFoundError**
```
❌ No module named 'mediapipe'
✅ Giải: pip install mediapipe opencv-python
```

**Lỗi 2: Camera không hoạt động**
```
❌ [ERROR] Cannot open camera
✅ Giải: python main.py --camera 1
```

**Lỗi 3: Gesture không được nhận diện**
```
❌ Tay di chuyển nhưng không có phản ứng
✅ Giải: 
   - Kiểm tra ánh sáng
   - Giảm min_detection_confidence
   - Tăng swipe_threshold thấp hơn
```

**Lỗi 4: Chương trình bị lag**
```
❌ FPS < 10
✅ Giải:
   - Giảm độ phân giải camera
   - Tăng min_tracking_confidence
   - Thắt gọn code trong vòng lặp
```

---

**🎓 Chúc các bạn học tập hiệu quả! 🚀**
