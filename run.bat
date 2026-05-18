@echo off
REM Script chạy ứng dụng trên Windows
REM Gesture Controlled Public Display System

echo.
echo ============================================================
echo     HE THONG BANG THONG TIN CONG CONG - DIEU KHIEN BANG CU CHI
echo ============================================================
echo.

REM Kiểm tra Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python khong tim thay!
    echo Vui long cai dat Python 3.8+ tu https://python.org
    pause
    exit /b 1
)

REM Kiểm tra requirements
echo [1/4] Kiem tra thu vien...
pip list | findstr "opencv-python" >nul
if errorlevel 1 (
    echo [!] Cai dat thu vien...
    pip install -q -r requirements.txt
)
echo [OK] Thu vien san sang

REM Tạo thư mục data nếu chưa có
if not exist data (
    mkdir data
    echo [OK] Tao thu muc data/
)

REM Chạy test
echo.
echo [2/4] Kiem tra cac module...
python test_modules.py
if errorlevel 1 (
    echo [ERROR] Test that bai!
    pause
    exit /b 1
)

REM Tạo dữ liệu mẫu nếu chưa có
echo.
echo [3/4] Chuan bi du lieu...
if not exist data\pages.json (
    python -c "from data_manager import DataManager; dm=DataManager(); dm.create_sample_data()"
)

REM Chạy ứng dụng
echo.
echo [4/4] Khoi dong ung dung...
echo.
python main.py %*

pause
