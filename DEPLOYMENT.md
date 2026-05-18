# 🚀 HƯỚNG DẪN DEPLOYMENT

## 1. Chuẩn bị Deployment

### ✅ Kiểm tra trước deployment
```bash
# 1. Test tất cả module
python test_modules.py

# 2. Kiểm tra lỗi import
python -c "import gesture, gui, config, data_manager"

# 3. Chạy ứng dụng một lần
python main.py --headless

# 4. Tạo dữ liệu mẫu
python -c "from data_manager import DataManager; DataManager().create_sample_data()"
```

### 📦 Package cho deployment
```bash
# Loại bỏ file không cần thiết
rm -rf __pycache__ .pytest_cache venv

# Tạo package
tar -czf gesture-display-v1.0.0.tar.gz *.py *.yaml *.md config requirements.txt data/

# Hoặc trên Windows
# (dùng 7-Zip, WinRAR, hoặc Ctrl+A → Send to → Compressed folder)
```

---

## 2. Cài đặt trên máy khác

### Windows
```cmd
# 1. Extract file
# 2. Mở Command Prompt
cd path\to\gesture-display
python setup.py
python test_modules.py
python main.py
```

### Mac/Linux
```bash
# 1. Extract file
# 2. Mở Terminal
cd gesture-display
chmod +x run.sh
./run.sh
```

---

## 3. Cấu hình cho Production

### Thay đổi config.yaml

```yaml
# Display - Full HD
display_width: 1920
display_height: 1080

# Camera - 1080p
camera_width: 1280
camera_height: 720
camera_fps: 30

# MediaPipe - Chính xác hơn
min_detection_confidence: 0.7
min_tracking_confidence: 0.7

# Data
data_dir: /var/lib/gesture-display/data
```

### Tạo dữ liệu sản xuất
```python
from data_manager import DataManager
from gui import Page

dm = DataManager("/var/lib/gesture-display/data")

# Thêm nội dung thực tế
pages = [
    Page(title="Sân bay", content="..."),
    Page(title="Đường bay", content="..."),
    # ...
]

for page in pages:
    dm.add_page(page)
```

---

## 4. Chạy trên Kiosk (Fullscreen)

### Windows - Registry
```registry
; Tạo file autorun.reg
Windows Registry Editor Version 5.00

[HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Run]
"GestureDisplay"="C:\\path\\to\\python.exe C:\\path\\to\\main.py --fullscreen"
```

### Linux - Systemd Service
```ini
# /etc/systemd/system/gesture-display.service
[Unit]
Description=Gesture Controlled Display System
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/opt/gesture-display
ExecStart=/usr/bin/python3 /opt/gesture-display/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Kích hoạt service
```bash
sudo systemctl daemon-reload
sudo systemctl enable gesture-display
sudo systemctl start gesture-display
```

---

## 5. Theo dõi & Logging

### Chuyển hướng output
```bash
# Linux/Mac
python main.py > logs/display.log 2>&1 &

# Windows (PowerShell)
python main.py | Out-File -FilePath logs\display.log -Append
```

### Cấu hình logging
```python
# Thêm vào main.py
import logging

logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

---

## 6. Cập nhật & Bảo trì

### Backup dữ liệu
```bash
# Linux/Mac
cp -r data data.backup
tar -czf data.backup.tar.gz data.backup/

# Windows
# Backup thư mục data/
```

### Cập nhật code
```bash
# 1. Backup dữ liệu
cp -r data data.backup

# 2. Extract version mới
tar -xzf gesture-display-v1.1.0.tar.gz

# 3. Restore dữ liệu
cp -r data.backup/* data/

# 4. Kiểm tra
python test_modules.py
```

---

## 7. Performance Tuning

### Tối ưu hóa cho Pi 4 (Raspberry Pi)
```yaml
# config.yaml
camera_width: 320
camera_height: 240
camera_fps: 20

display_width: 800
display_height: 480

min_detection_confidence: 0.6
min_tracking_confidence: 0.6
```

### Giảm CPU usage
```bash
# Chạy với lower priority
nice -n 10 python main.py

# hoặc
taskset -c 0,1 python main.py  # Dùng 2 cores
```

---

## 8. Troubleshooting Deployment

### Vấn đề | Giải pháp
```
❌ Import error        → Kiểm tra requirements
❌ Camera không mở     → Kiểm tra permission
❌ Chậm               → Giảm resolution, tăng detection threshold
❌ Crash              → Kiểm tra logs
❌ Hết bộ nhớ        → Kiểm tra rò rỉ memory
```

---

## 9. Monitoring

### Health check script
```python
#!/usr/bin/env python3
# health_check.py

import subprocess
import time
import requests

def check_process():
    result = subprocess.run(['pgrep', '-f', 'main.py'], 
                          capture_output=True)
    return result.returncode == 0

def restart_service():
    subprocess.run(['systemctl', 'restart', 'gesture-display'])

while True:
    if not check_process():
        print("Process dead, restarting...")
        restart_service()
    time.sleep(60)
```

### Chuẩn bị cron job
```bash
# Crontab: Chạy health check mỗi phút
* * * * * /usr/bin/python3 /opt/gesture-display/health_check.py
```

---

## 10. Security

### Bảo vệ cấu hình
```bash
# Linux/Mac
chmod 600 config.yaml          # Chỉ owner có thể đọc
chmod 700 data/                # Chỉ owner có thể truy cập

# Windows
# icacls config.yaml /grant:r User:F /inheritance:r
```

### Tắt debugging trên production
```yaml
# config.yaml
debug_mode: false
```

---

## 📋 Deployment Checklist

- [ ] Tất cả test pass
- [ ] Config kiểm tra
- [ ] Dữ liệu backup
- [ ] Script chạy được
- [ ] Logging hoạt động
- [ ] Monitoring sắp sàng
- [ ] Performance ok
- [ ] Security check

---

**Chúc deployment thành công! 🚀**
