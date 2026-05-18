"""
Script setup và chuẩn bị environment
Tạo dữ liệu mẫu, kiểm tra thư viện, v.v.
"""

import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Kiểm tra phiên bản Python"""
    print("Kiểm tra Python version...")
    
    major, minor = sys.version_info[:2]
    version_str = f"{major}.{minor}"
    
    if major < 3 or (major == 3 and minor < 8):
        print(f"❌ Lỗi: Cần Python 3.8+, hiện có {version_str}")
        return False
    
    print(f"✓ Python {version_str} (OK)")
    return True


def check_and_install_packages():
    """Kiểm tra và cài đặt thư viện"""
    print("\nCài đặt thư viện...")
    
    packages = [
        "opencv-python>=4.5.0",
        "mediapipe>=0.8.0",
        "numpy>=1.19.0",
        "PyYAML>=5.4.0"
    ]
    
    for package in packages:
        print(f"  Kiểm tra {package.split('>=')[0]}...", end=" ")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "-q", package],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print("✓")
        except subprocess.CalledProcessError:
            print("❌")
            return False
    
    return True


def create_directories():
    """Tạo các thư mục cần thiết"""
    print("\nTạo thư mục...")
    
    dirs = [
        "data",
        "assets",
        "logs"
    ]
    
    for dir_name in dirs:
        path = Path(dir_name)
        path.mkdir(exist_ok=True)
        print(f"  ✓ {dir_name}/")
    
    return True


def create_sample_data():
    """Tạo dữ liệu mẫu"""
    print("\nTạo dữ liệu mẫu...")
    
    try:
        from data_manager import DataManager
        
        dm = DataManager()
        pages = dm.get_sample_pages()
        dm.save_pages(pages)
        
        print(f"  ✓ Đã tạo {len(pages)} trang mẫu")
        return True
    
    except Exception as e:
        print(f"  ❌ Lỗi: {e}")
        return False


def test_imports():
    """Kiểm tra có thể import các module"""
    print("\nKiểm tra imports...")
    
    modules = [
        "cv2",
        "mediapipe",
        "numpy",
        "yaml"
    ]
    
    for module in modules:
        try:
            __import__(module)
            print(f"  ✓ {module}")
        except ImportError:
            print(f"  ❌ {module} - không cài đặt")
            return False
    
    return True


def test_camera():
    """Kiểm tra camera"""
    print("\nKiểm tra camera...")
    
    try:
        import cv2
        
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("  ✓ Camera 0 - Sẵn sàng")
            cap.release()
            return True
        else:
            print("  ⚠ Camera 0 - Không sẵn sàng")
            print("    (Có thể sử dụng --camera để chỉ định camera khác)")
            return True  # Không fail, chỉ cảnh báo
    
    except Exception as e:
        print(f"  ❌ Lỗi kiểm tra camera: {e}")
        return False


def main():
    """Chạy setup"""
    print("\n")
    print("█" * 60)
    print("█" + " " * 58 + "█")
    print("█" + "  SETUP HỆ THỐNG BẢNG THÔNG TIN".center(58) + "█")
    print("█" + " " * 58 + "█")
    print("█" * 60)
    print()
    
    checks = [
        ("Python version", check_python_version),
        ("Thư viện Python", check_and_install_packages),
        ("Thư mục cần thiết", create_directories),
        ("Import modules", test_imports),
        ("Dữ liệu mẫu", create_sample_data),
        ("Camera", test_camera),
    ]
    
    all_passed = True
    for name, check_func in checks:
        try:
            if not check_func():
                all_passed = False
                print(f"  ❌ {name} FAILED")
                break
        except Exception as e:
            all_passed = False
            print(f"  ❌ {name} ERROR: {e}")
            break
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("✅ SETUP HOÀN THÀNH!")
        print("=" * 60)
        print("\n📌 Các bước tiếp theo:")
        print("  1. Đảm bảo đã cấu hình config.yaml nếu cần")
        print("  2. Chạy: python test_modules.py")
        print("  3. Chạy: python main.py")
        print("\n")
        return 0
    else:
        print("❌ SETUP THẤT BẠI!")
        print("=" * 60)
        print("\nVui lòng kiểm tra lỗi phía trên\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
