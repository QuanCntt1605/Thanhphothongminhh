#!/bin/bash
# Script chạy ứng dụng trên Mac/Linux
# Gesture Controlled Public Display System

echo ""
echo "============================================================"
echo "    HE THONG BANG THONG TIN CONG CONG - DIEU KHIEN BANG CU CHI"
echo "============================================================"
echo ""

# Kiểm tra Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python khong tim thay!"
    echo "Vui long cai dat Python 3.8+ tu https://python.org"
    exit 1
fi

# Kiểm tra requirements
echo "[1/4] Kiem tra thu vien..."
if ! pip3 list | grep -q "opencv-python"; then
    echo "[!] Cai dat thu vien..."
    pip3 install -q -r requirements.txt
fi
echo "[OK] Thu vien san sang"

# Tạo thư mục data nếu chưa có
if [ ! -d "data" ]; then
    mkdir -p data
    echo "[OK] Tao thu muc data/"
fi

# Chạy test
echo ""
echo "[2/4] Kiem tra cac module..."
python3 test_modules.py
if [ $? -ne 0 ]; then
    echo "[ERROR] Test that bai!"
    exit 1
fi

# Tạo dữ liệu mẫu nếu chưa có
echo ""
echo "[3/4] Chuan bi du lieu..."
if [ ! -f "data/pages.json" ]; then
    python3 -c "from data_manager import DataManager; dm=DataManager(); dm.create_sample_data()"
fi

# Chạy ứng dụng
echo ""
echo "[4/4] Khoi dong ung dung..."
echo ""
python3 main.py "$@"
