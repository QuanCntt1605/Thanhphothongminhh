"""
Hệ thống điều khiển bảng thông tin công cộng không chạm bằng cử chỉ
Sử dụng MediaPipe để nhận diện tay và gesture điều khiển

Tác giả: Sinh viên
Ngày: 2026
"""

import cv2
import sys
import argparse
from typing import Optional
from pathlib import Path

from gesture import GestureRecognizer, GestureType
from gui import DisplayGUI, Page
from config import Config
from data_manager import DataManager


class GestureControlledDisplay:
    """Hệ thống bảng thông tin điều khiển bằng cử chỉ"""
    
    def __init__(self, 
                 config_path: Optional[str] = None,
                 camera_id: int = 0,
                 headless: bool = False):
        """
        Khởi tạo hệ thống
        
        Args:
            config_path: Đường dẫn đến file cấu hình
            camera_id: ID của camera
            headless: Chế độ không có giao diện (chỉ xử lý)
        """
        self.config = Config.load(config_path)
        self.gesture_recognizer = GestureRecognizer(
            min_detection_confidence=self.config.min_detection_confidence,
            min_tracking_confidence=self.config.min_tracking_confidence
        )
        self.display = DisplayGUI(
            width=self.config.display_width,
            height=self.config.display_height,
            font_scale=self.config.font_scale
        )
        
        # Camera
        self.camera_id = camera_id
        self.cap = None
        self.headless = headless
        
        # Data manager
        self.data_manager = DataManager(self.config.data_dir)
        
        # Thống kê
        self.frame_count = 0
        self.gesture_count = {g.value: 0 for g in GestureType}
        
        # State
        self.running = True
        self.show_debug = False
        self.pause = False
        self.gesture_cooldown = 0
        
    def load_content(self):
        """Tải nội dung từ data manager"""
        pages = self.data_manager.load_pages()
        for page in pages:
            self.display.add_page(page)
        
        if len(pages) > 0:
            print(f"✓ Đã tải {len(pages)} trang nội dung")
        else:
            print("⚠ Không có nội dung, tạo nội dung mặc định")
            self._create_default_content()
    
    def _create_default_content(self):
        """Tạo nội dung mặc định cho demo"""
        page1 = Page(
            title="Chào mừng",
            content="""Hệ thống bảng thông tin công cộng không chạm
            
Điều khiển bằng cử chỉ tay:
• Vuốt trái/phải: Chuyển trang
• Cuộn lên/xuống: Cuộn nội dung
• Hai tay lại gần: Zoom in
• Hai tay tách ra: Zoom out"""
        )
        
        page2 = Page(
            title="Hướng dẫn sử dụng",
            content="""Các cử chỉ được hỗ trợ:

1. VUỐT SANG PHẢI: Trang trước đó
2. VUỐT SANG TRÁI: Trang tiếp theo
3. CUỘN LÊN: Cuộn nội dung lên
4. CUỘN XUỐNG: Cuộn nội dung xuống
5. ZOOM IN: Phóng to (hai tay gập lại)
6. ZOOM OUT: Thu nhỏ (hai tay tách ra)

Nhấn 'D' để hiển thị debug
Nhấn 'P' để tạm dừng/tiếp tục
Nhấn 'Q' hoặc 'ESC' để thoát"""
        )
        
        page3 = Page(
            title="Ứng dụng thực tế",
            content="""Bảng thông tin này có thể áp dụng tại:

✓ Sân bay (Hướng dẫn đường bay)
✓ Trung tâm thương mại (Bản đồ, danh sách cửa hàng)
✓ Bệnh viện (Thông tin khoa phòng)
✓ Trường học (Thời khóa biểu, thông báo)
✓ Nhà ga (Thời gian xe, giá vé)
✓ Phòng vé (Suất chiếu, đặt vé)
✓ Bảo tàng (Thông tin triển lãm)"""
        )
        
        self.display.add_page(page1)
        self.display.add_page(page2)
        self.display.add_page(page3)
    
    def handle_gesture(self, gesture_type: GestureType):
        """Xử lý cử chỉ"""
        if gesture_type == GestureType.NONE or self.pause:
            return
        
        # Cập nhật thống kê
        self.gesture_count[gesture_type.value] += 1
        
        if gesture_type == GestureType.SWIPE_RIGHT:
            print("← Vuốt phải: Trang trước")
            self.display.previous_page()
        
        elif gesture_type == GestureType.SWIPE_LEFT:
            print("→ Vuốt trái: Trang tiếp theo")
            self.display.next_page()
        
        elif gesture_type == GestureType.ZOOM_IN:
            print("🔍 Zoom in")
            self.display.zoom_in()
        
        elif gesture_type == GestureType.ZOOM_OUT:
            print("🔍 Zoom out")
            self.display.zoom_out()
        
        elif gesture_type == GestureType.SCROLL_UP:
            print("⬆ Cuộn lên")
            self.display.scroll_up()
        
        elif gesture_type == GestureType.SCROLL_DOWN:
            print("⬇ Cuộn xuống")
            self.display.scroll_down()
        
        elif gesture_type == GestureType.GRAB:
            print("✋ Nắm tay (Grab)")
    
    def process_keyboard(self, key: int):
        """Xử lý bàn phím"""
        if key == ord('q') or key == 27:  # Q hoặc ESC
            print("\nThoát chương trình...")
            self.running = False
        
        elif key == ord('d'):
            self.show_debug = not self.show_debug
            status = "BẬT" if self.show_debug else "TẮT"
            print(f"Debug: {status}")
        
        elif key == ord('p'):
            self.pause = not self.pause
            status = "TẠMỪNG" if self.pause else "TIẾPTỤC"
            print(f"Trạng thái: {status}")
        
        elif key == ord('r'):
            print("Reset view...")
            self.display.reset_view()
        
        elif key == ord('n'):
            print("Trang tiếp theo...")
            self.display.next_page()
        
        elif key == ord('b'):
            print("Trang trước...")
            self.display.previous_page()
    
    def run(self):
        """Chạy hệ thống chính"""
        print("=" * 60)
        print("HỆ THỐNG BẢNG THÔNG TIN CÔNG CỘNG")
        print("Điều khiển bằng cử chỉ tay")
        print("=" * 60)
        
        # Tải nội dung
        self.load_content()
        
        if self.headless:
            print("Chế độ headless - không hiển thị camera")
            return
        
        # Mở camera
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            
            if not self.cap.isOpened():
                print(f"❌ Lỗi: Không thể mở camera {self.camera_id}")
                return
            
            # Cấu hình camera
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.camera_width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.camera_height)
            self.cap.set(cv2.CAP_PROP_FPS, self.config.camera_fps)
            
            print(f"✓ Camera bật thành công")
            print(f"✓ Độ phân giải: {self.config.camera_width}x{self.config.camera_height}")
            print("\nPhím tắt:")
            print("  D - Hiển thị debug")
            print("  P - Tạm dừng/Tiếp tục")
            print("  R - Reset view")
            print("  N - Trang tiếp theo")
            print("  B - Trang trước")
            print("  Q - Thoát")
            print("\n" + "=" * 60 + "\n")
            
            while self.running:
                success, frame = self.cap.read()
                
                if not success:
                    print("❌ Lỗi: Không thể đọc từ camera")
                    break
                
                self.frame_count += 1
                
                # Lật camera ngang (thường cần với webcam)
                frame = cv2.flip(frame, 1)
                
                # Xử lý gesture
                gesture_frame = self.gesture_recognizer.process_frame(frame)
                
                # Xử lý cử chỉ
                if gesture_frame.gesture != GestureType.NONE:
                    self.handle_gesture(gesture_frame.gesture)
                
                # Vẽ landmarks trên camera preview
                camera_display = self.gesture_recognizer.draw_landmarks(
                    frame, gesture_frame
                )
                
                # Thay đổi kích thước camera preview
                camera_preview = cv2.resize(
                    camera_display,
                    (self.config.camera_preview_width, 
                     self.config.camera_preview_height)
                )
                
                # Render giao diện bảng thông tin
                info_display = self.display.render(show_debug=self.show_debug)
                
                # Ghép camera preview vào góc của info display
                x_offset = self.config.display_width - self.config.camera_preview_width - 10
                y_offset = 10
                
                info_display[y_offset:y_offset + self.config.camera_preview_height,
                            x_offset:x_offset + self.config.camera_preview_width] = camera_preview
                
                # Vẽ khung cho camera preview
                cv2.rectangle(
                    info_display,
                    (x_offset - 2, y_offset - 2),
                    (x_offset + self.config.camera_preview_width + 2,
                     y_offset + self.config.camera_preview_height + 2),
                    (0, 255, 255), 3
                )
                
                # Hiển thị gesture hiện tại
                if gesture_frame.gesture != GestureType.NONE:
                    gesture_text = f"Gesture: {gesture_frame.gesture.value}"
                    cv2.putText(
                        info_display,
                        gesture_text,
                        (20, 100),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 255, 0),
                        2
                    )
                
                # Hiển thị status pause
                if self.pause:
                    cv2.putText(
                        info_display,
                        "TАМDUNG",
                        (self.config.display_width // 2 - 100, 100),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.5,
                        (0, 0, 255),
                        3
                    )
                
                # Hiển thị
                cv2.imshow("Gesture Controlled Display", info_display)
                
                # Xử lý bàn phím
                key = cv2.waitKey(1) & 0xFF
                if key != 255:
                    self.process_keyboard(key)
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Dọn dẹp tài nguyên"""
        print("\n" + "=" * 60)
        print("THỐNG KÊ")
        print("=" * 60)
        print(f"Tổng số khung hình: {self.frame_count}")
        print(f"Tổng số cử chỉ: {sum(self.gesture_count.values())}")
        print("\nBiểu đồ cử chỉ:")
        for gesture, count in self.gesture_count.items():
            if count > 0:
                print(f"  {gesture}: {count}")
        
        if self.cap:
            self.cap.release()
        
        cv2.destroyAllWindows()
        print("\n✓ Chương trình kết thúc")


def main():
    """Hàm chính"""
    parser = argparse.ArgumentParser(
        description="Hệ thống bảng thông tin công cộng điều khiển bằng cử chỉ"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Đường dẫn file cấu hình (mặc định: config.yaml)"
    )
    parser.add_argument(
        "--camera",
        type=int,
        default=0,
        help="ID camera (mặc định: 0)"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Chế độ không có giao diện"
    )
    
    args = parser.parse_args()
    
    app = GestureControlledDisplay(
        config_path=args.config,
        camera_id=args.camera,
        headless=args.headless
    )
    
    app.run()


if __name__ == "__main__":
    main()