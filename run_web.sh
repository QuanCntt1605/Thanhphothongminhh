#!/bin/bash

# Khởi động Bảng Thông Tin Công Cộng - Web Version
# Yêu cầu: Python 3.8+ và Flask đã cài

echo "============================================================"
echo "BẢNG THÔNG TIN CÔNG CỘNG - WEB VERSION"
echo "============================================================"
echo

# Kích hoạt virtual environment nếu có
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✓ Virtual environment activated"
    echo
fi

# Cài đặt Flask nếu chưa có
python3 -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing Flask..."
    pip install Flask Werkzeug
fi

# Chạy web server
echo "============================================================"
echo "Khởi động web server..."
echo
echo "📱 Mở trình duyệt và truy cập:"
echo "   http://localhost:5000"
echo
echo "🌐 Hoặc từ máy khác:"
echo "   http://<IP_ADDRESS>:5000"
echo
echo "Nhấn Ctrl+C để dừng server"
echo "============================================================"
echo

python3 app_web.py
