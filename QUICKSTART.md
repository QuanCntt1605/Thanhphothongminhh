# 🎯 QUICK START GUIDE
## Hướng dẫn bắt đầu nhanh

### 1️⃣ CÀI ĐẶT (2 phút)

**Windows:**
```bash
# Mở Command Prompt (Ctrl+R → cmd)
cd C:\Users\MSI\Downloads\Thành phố thông minh
python setup.py
```

**Mac/Linux:**
```bash
cd ~/Downloads/Thành\ phố\ thông\ minh
python3 setup.py
```

### 2️⃣ KIỂM TRA (1 phút)

```bash
python test_modules.py
# Nếu thấy "✅ TẤT CẢ TEST PASSED!" → OK
```

### 3️⃣ CHẠY ỨNG DỤNG (Ngay!)

```bash
python main.py
```

**Bạn sẽ thấy:**
- 📹 Cửa sổ hiển thị bảng thông tin
- 📷 Camera preview ở góc phải
- 📱 Bảng thông tin chính ở giữa

---

## 🎮 ĐIỀU KHIỂN (30 giây để hiểu)

### Cử chỉ tay
```
👆 Tay lên/xuống → Cuộl
👉 Tay sang trái/phải → Chuyển trang  
👐 2 tay → Zoom (lại gần = phóng to, tách ra = thu nhỏ)
✊ Nắm tay → Grab
```

### Phím bàn phím
```
D = Debug    P = Tạm dừng    Q = Thoát
N = Trang+   B = Trang-     R = Reset
```

---

## 📋 CÓ VẤN ĐỀ?

### Camera không hoạt động
```bash
python main.py --camera 1
# hoặc camera 2, 3, etc.
```

### Gesture không nhận diện
- 🔆 Tăng ánh sáng
- Sửa `config.yaml` → `min_detection_confidence: 0.3`

### Chương trình chậm
- Sửa `config.yaml` → `camera_width: 320`

---

## 📚 MUỐN HỌC THÊM?

Đọc:
- 📖 **README.md** - Hướng dẫn đầy đủ
- 📚 **GUIDE.md** - Chi tiết kỹ thuật
- 📌 **PROJECT_SUMMARY.md** - Tóm tắt dự án

---

## ✨ CÁC FILE CHÍNH

| File | Mục đích |
|------|----------|
| **main.py** | Ứng dụng chính |
| **gesture.py** | Nhận diện cử chỉ |
| **gui.py** | Giao diện |
| **config.yaml** | Cấu hình |
| **data/pages.json** | Nội dung |

---

## 🚀 CHÚC BẠN SỬ DỤNG THÀNH CÔNG!

Có thắc mắc? Xem **GUIDE.md** hoặc **README.md**

---

*Made with ❤️ for Education*
