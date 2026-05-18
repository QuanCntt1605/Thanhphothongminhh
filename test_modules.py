"""
Script test và demo các tính năng
"""

import sys
from pathlib import Path

# Thêm thư mục hiện tại vào path
sys.path.insert(0, str(Path(__file__).parent))

from gesture import GestureRecognizer, GestureType
from gui import DisplayGUI, Page
from config import Config
from data_manager import DataManager


def test_gesture_recognizer():
    """Test module nhận diện cử chỉ"""
    print("=" * 60)
    print("TEST: Gesture Recognizer")
    print("=" * 60)
    
    recognizer = GestureRecognizer()
    print(f"✓ GestureRecognizer khởi tạo thành công")
    print(f"  History length: {recognizer.history_max_length}")
    print(f"  Swipe threshold: {recognizer.swipe_threshold}px")
    print(f"  Zoom threshold: {recognizer.zoom_threshold}px")
    
    # Test distance calculation
    dist = recognizer.get_distance((0, 0), (3, 4))
    assert dist == 5.0, "Distance calculation failed"
    print(f"✓ Distance calculation: OK (3-4-5 triangle = {dist})")
    
    print()


def test_gui():
    """Test module giao diện"""
    print("=" * 60)
    print("TEST: Display GUI")
    print("=" * 60)
    
    display = DisplayGUI(width=1280, height=720)
    print(f"✓ DisplayGUI khởi tạo thành công")
    print(f"  Resolution: {display.width}x{display.height}")
    print(f"  Zoom range: {display.min_zoom}x - {display.max_zoom}x")
    
    # Thêm trang
    page1 = Page(title="Test Page 1", content="This is test content for page 1")
    page2 = Page(title="Test Page 2", content="This is test content for page 2")
    
    display.add_page(page1)
    display.add_page(page2)
    print(f"✓ Đã thêm {display.get_page_count()} trang")
    
    # Test navigation
    display.next_page()
    assert display.get_current_page_index() == 1
    print(f"✓ next_page(): OK (trang hiện tại: {display.get_current_page_index() + 1})")
    
    display.previous_page()
    assert display.get_current_page_index() == 0
    print(f"✓ previous_page(): OK (trang hiện tại: {display.get_current_page_index() + 1})")
    
    # Test zoom
    original_zoom = display.zoom_level
    display.zoom_in()
    assert display.zoom_level > original_zoom
    print(f"✓ zoom_in(): {original_zoom:.1f}x → {display.zoom_level:.1f}x")
    
    display.zoom_out()
    assert display.zoom_level == original_zoom
    print(f"✓ zoom_out(): {display.zoom_level:.1f}x")
    
    print()


def test_config():
    """Test module cấu hình"""
    print("=" * 60)
    print("TEST: Configuration")
    print("=" * 60)
    
    # Default config
    config = Config()
    print(f"✓ Config khởi tạo với giá trị mặc định")
    print(f"  Display: {config.display_width}x{config.display_height}")
    print(f"  Camera: {config.camera_width}x{config.camera_height} @ {config.camera_fps}fps")
    print(f"  Detection confidence: {config.min_detection_confidence}")
    
    # Try to load config.yaml
    config_from_file = Config.load("config.yaml")
    assert config_from_file is not None
    print(f"✓ Loaded config từ config.yaml")
    
    print()


def test_data_manager():
    """Test module quản lý dữ liệu"""
    print("=" * 60)
    print("TEST: Data Manager")
    print("=" * 60)
    
    dm = DataManager(data_dir="test_data")
    print(f"✓ DataManager khởi tạo")
    print(f"  Data dir: {dm.data_dir}")
    
    # Get sample pages
    sample_pages = dm.get_sample_pages()
    print(f"✓ Lấy {len(sample_pages)} trang mẫu")
    for i, page in enumerate(sample_pages, 1):
        print(f"  - Trang {i}: {page.title}")
    
    print()


def test_all():
    """Chạy tất cả test"""
    print("\n")
    print("█" * 60)
    print("█" + " " * 58 + "█")
    print("█" + "  KIỂM TRA CÁC MODULE (TEST SUITE)".center(58) + "█")
    print("█" + " " * 58 + "█")
    print("█" * 60)
    print()
    
    try:
        test_gesture_recognizer()
        test_gui()
        test_config()
        test_data_manager()
        
        print("=" * 60)
        print("✅ TẤT CẢ TEST PASSED!")
        print("=" * 60)
        print("\n✓ Tất cả module hoạt động bình thường")
        print("✓ Sẵn sàng để chạy main.py\n")
        
        return True
    
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ TEST FAILED: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_all()
    sys.exit(0 if success else 1)
