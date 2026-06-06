@echo off
REM Khởi động Bảng Thông Tin Công Cộng - Web Version
REM
REM Yêu cầu: Python 3.8+ và Flask đã cài
REM

echo ============================================================
echo BẢNG THÔNG TIN CÔNG CỘNG - WEB VERSION
echo ============================================================
echo.

REM Kích hoạt virtual environment nếu có
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo ✓ Virtual environment activated
    echo.
)

REM Cài đặt Flask nếu chưa có
pip show Flask >nul 2>&1
if errorlevel 1 (
    echo Installing Flask...
    pip install Flask Werkzeug
)

REM Chạy web server
echo ============================================================
echo Khởi động web server...
echo.
echo 📱 Mở trình duyệt và truy cập:
echo    http://localhost:5000
echo.
echo 🌐 Hoặc từ máy khác:
echo    http://<IP_ADDRESS>:5000
echo.
echo Nhấn Ctrl+C để dừng server
echo ============================================================
echo.

python app_web.py

pause
