"""
Hệ thống điều khiển bảng thông tin công cộng không chạm bằng cử chỉ
Sử dụng MediaPipe để nhận diện tay và gesture điều khiển

Tác giả: Sinh viên
Ngày: 2026
"""

import cv2
import numpy as np
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
                 headless: bool = False,
                 demo: bool = False):
        """
        Khởi tạo hệ thống
        
        Args:
            config_path: Đường dẫn đến file cấu hình
            camera_id: ID của camera
            headless: Chế độ không có giao diện (chỉ xử lý)
            demo: Chế độ demo (không cần camera)
        """
        self.config = Config.load(config_path)
        self.gesture_recognizer = None  # Khởi tạo lazy khi cần
        self.display = DisplayGUI(
            width=self.config.display_width,
            height=self.config.display_height,
            font_scale=self.config.font_scale
        )
        
        # Camera
        self.camera_id = camera_id
        self.cap = None
        self.headless = headless
        self.demo = demo
        
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
    
    def _init_gesture_recognizer(self):
        """Khởi tạo GestureRecognizer một lần"""
        if self.gesture_recognizer is None:
            print("🔧 Khởi tạo GestureRecognizer...")
            self.gesture_recognizer = GestureRecognizer(
                min_detection_confidence=self.config.min_detection_confidence,
                min_tracking_confidence=self.config.min_tracking_confidence
            )
        
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
        # Trang 1: Chào mừng
        page1 = Page(
            title="🎉 Chào mừng",
            content="""Hệ thống bảng thông tin công cộng không chạm

✋ Điều khiển bằng cử chỉ tay:
→ Vuốt trái/phải: Chuyển trang
↕ Cuộn lên/xuống: Cuộn nội dung
🔍 Hai tay gần/xa: Zoom in/out"""
        )
        
        # Trang 2: Hướng dẫn sử dụng chi tiết
        page2 = Page(
            title="📚 Hướng dẫn sử dụng",
            content="""CÁCH ĐIỀU KHIỂN:

1️⃣ VUỐT SANG PHẢI
   Quay về trang trước

2️⃣ VUỐT SANG TRÁI  
   Đi đến trang tiếp theo

3️⃣ CUỘN LÊN
   Xem nội dung phía trên

4️⃣ CUỘL XUỐNG
   Xem nội dung phía dưới

5️⃣ ZOOM IN
   Phóng to (hai tay gập lại)

6️⃣ ZOOM OUT
   Thu nhỏ (hai tay tách ra)

💡 Phím tắt:
D - Debug | P - Tạm dừng | Q - Thoát"""
        )
        
        # Trang 3: Ứng dụng thực tế
        page3 = Page(
            title="🏢 Ứng dụng thực tế",
            content="""Bảng thông tin này có thể áp dụng tại:

✈️ SÂN BAY
   • Hướng dẫn đường bay
   • Thông tin chuyến bay
   • Bản đồ sân bay

🏬 TRUNG TÂM THƯƠNG MẠI
   • Danh sách cửa hàng
   • Bản đồ tòa nhà
   • Quảng cáo sản phẩm

🏥 BỆNH VIỆN
   • Thông tin khoa phòng
   • Hướng dẫn bộ phận
   • Lịch làm việc"""
        )
        
        # Trang 4: Đặc tính kỹ thuật
        page4 = Page(
            title="🔧 Đặc tính kỹ thuật",
            content="""CÔNG NGHỆ SỬ DỤNG:

🎥 OpenCV
   • Xử lý video real-time
   • Độ phân giải cao
   • Hiệu suất tối ưu

✋ MediaPipe
   • Nhận diện tay chính xác
   • Phát hiện 21 điểm khớp
   • Hoạt động 2 tay

📱 Python
   • Framework linh hoạt
   • Hỗ trợ đa nền tảng
   • Mã nguồn mở

⚡ HIỆU NĂNG:
   • 30+ FPS
   • Độ trễ < 100ms
   • Tiết kiệm năng lượng"""
        )
        
        # Trang 5: Hướng dẫn chi tiết
        page5 = Page(
            title="📖 Hướng dẫn chi tiết",
            content="""CÁCH SỬ DỤNG HỆ THỐNG:

🟢 KHỞI ĐỘNG:
   1. Đứng cách camera 1-2 mét
   2. Hệ thống tự nhận diện tay
   3. Khung xanh = sẵn sàng

🔵 ĐIỀU HƯỚNG:
   • Vuốt nhanh để chuyển trang
   • Cuộn từ từ để xem chi tiết
   • Zoom để xem rõ hơn

🟡 THỦ CÔNG:
   • Giữ tay trong khung
   • Chuyển động rõ ràng
   • Tránh nhanh quá

🔴 KHẮC PHỤC:
   • Không phát hiện: Dùng -demo
   • Lag: Giảm độ phân giải
   • Lỗi: Restart hệ thống"""
        )
        
        # Trang 6: Thông tin liên hệ
        page6 = Page(
            title="📞 Thông tin & Liên hệ",
            content="""THÔNG TIN HỆ THỐNG:

📊 PHIÊN BẢN: 2.0
🔄 CẬP NHẬT: 2026
👤 PHÁT TRIỂN: Nhóm sinh viên
🌐 NGÔN NGỮ: Tiếng Việt

📧 LIÊN HỆ HỖTRỢ:
   • Email: support@example.com
   • Phone: +84 (0) 123 456 789
   • Website: www.example.com

📋 LICENCE:
   MIT Open Source
   
⭐ CẢM ƠN SỬ DỤNG!"""
        )
        
        # Trang 7: Tips & Mẹo
        page7 = Page(
            title="💡 Mẹo & Thủ thuật",
            content="""MẸOCHO TRẢI NGHIỆM TỐT NHẤT:

✅ CÓ NÊN LÀM:
   • Giữ tay trong góc camera
   • Di chuyển tay rõ ràng
   • Sử dụng ánh sáng tốt
   • Giũ tay sạch

❌ KHÔNG NÊN LÀM:
   • Chuyển động quá nhanh
   • Tay ẩn phía sau cơ thể
   • Ánh sáng quá tối
   • Tay bẩn/ở trong bóng

🎯 CHỈ BẬC MỠ TỐTCHẤT:
   1. Tay rõ ràng
   2. Ánh sáng đủ
   3. Khoảng cách vừa phải
   4. Chuyển động tự nhiên"""
        )
        
        # Trang 8: Lịch sử & Phát triển
        page8 = Page(
            title="📅 Lịch sử phát triển",
            content="""QUÁTRÌNH PHÁT TRIỂN:

V1.0 (2025)
• Hệ thống cơ bản
• Nhận diện tay đơn giản
• 3 cử chỉ cơ bản
• GUI tối giản

V1.5 (Mid-2025)
• Thêm zoom gesture
• GUI cải thiện
• Hỗ trợ đa trang
• Tối ưu hiệu năng

V2.0 (2026) ✨ HIỆN TẠI
• Nhận diện 8+ cử chỉ
• GUI hiện đại
• Khung hiển thị tay
• Đa ngôn ngữ
• Tối ưu AI

V3.0 (Sắp tới)
• Bàn phím ảo
• Nhận dạng khuôn mặt
• Hỗ trợ giọng nói"""
        )
        
        # Trang 9: Hỗ trợ sự cố
        page9 = Page(
            title="🆘 Hỗ trợ sự cố",
            content="""GIẢI PHÁP CHO VẤN ĐỀ THƯỜNG GẶP:

❓ VẤNĐỀ: Không phát hiện tay

✅ GIẢI PHÁP:
   1. Kiểm tra camera hoạt động
   2. Thử --demo mode
   3. Tăng ánh sáng
   4. Di chuyển tay từ từ
   5. Khởi động lại hệ thống

❓ VẤNĐỀ: Gesture không nhận

✅ GIẢI PHÁP:
   1. Chuyển động rõ ràng
   2. Tay trong khung
   3. Không quá nhanh
   4. Nhấn phím D để xem debug

❓ VẤNĐỀ: Lag/Chậm

✅ GIẢI PHÁP:
   1. Giảm độ phân giải camera
   2. Đóng ứng dụng khác
   3. Kiểm tra CPU
   4. Update driver camera"""
        )
        
        # Thêm tất cả trang
        pages = [page1, page2, page3, page4, page5, page6, page7, page8, page9]
        for page in pages:
            self.display.add_page(page)
        
        print(f"✓ Đã tạo {len(pages)} trang nội dung mặc định")
    
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
        
        # Nếu là demo mode, không cần camera
        if self.demo:
            print("🎬 CHẾ ĐỘ DEMO (Không dùng camera)")
            self.run_demo_mode()
            return
        
        # Khởi tạo gesture recognizer trước khi dùng
        self._init_gesture_recognizer()
        
        # Mở camera
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            
            if not self.cap.isOpened():
                print(f"❌ Lỗi: Không thể mở camera {self.camera_id}")
                print("💡 Gợi ý: Chạy với --demo để test chế độ demo")
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
                
                # Render giao diện bảng thông tin với gesture indicator
                info_display = self.display.render(
                    show_debug=self.show_debug,
                    last_gesture=gesture_frame.gesture if gesture_frame.gesture != GestureType.NONE else None
                )
                
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
    
    def run_demo_mode(self):
        """Chạy chế độ demo (không dùng camera)"""
        print("✓ Chế độ demo khởi động")
        print("\nPhím tắt:")
        print("  D - Hiển thị debug")
        print("  P - Tạm dừng/Tiếp tục")
        print("  R - Reset view")
        print("  N - Trang tiếp theo")
        print("  B - Trang trước")
        print("  Q - Thoát")
        print("  + - Phóng to")
        print("  - - Thu nhỏ")
        print("  ↑ - Cuộn lên")
        print("  ↓ - Cuộn xuống")
        print("\n" + "=" * 60 + "\n")
        
        import time
        start_time = time.time()
        
        try:
            while self.running:
                self.frame_count += 1
                
                # Tạo frame demo (màn hình xanh đầu tiên)
                demo_frame = np.zeros((self.config.camera_height, self.config.camera_width, 3), dtype=np.uint8)
                demo_frame[:] = (50, 50, 100)  # Màu xanh đậm
                
                # Thêm text "DEMO MODE"
                cv2.putText(
                    demo_frame,
                    "DEMO MODE",
                    (self.config.camera_width // 2 - 150, self.config.camera_height // 2),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    2,
                    (0, 255, 255),
                    3
                )
                
                # Thay đổi kích thước camera preview
                camera_preview = cv2.resize(
                    demo_frame,
                    (self.config.camera_preview_width, 
                     self.config.camera_preview_height)
                )
                
                # Render giao diện bảng thông tin
                info_display = self.display.render(show_debug=self.show_debug, last_gesture=None)
                
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
                
                # Hiển thị status pause
                if self.pause:
                    cv2.putText(
                        info_display,
                        "TAM DUNG",
                        (self.config.display_width // 2 - 100, 100),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.5,
                        (0, 0, 255),
                        3
                    )
                
                # Hiển thị
                cv2.imshow("Gesture Controlled Display - DEMO MODE", info_display)
                
                # Xử lý bàn phím
                key = cv2.waitKey(30) & 0xFF
                if key != 255:
                    if key == ord('+') or key == ord('='):
                        self.display.zoom_in()
                        print("🔍 Phóng to:", self.display.zoom_level)
                    elif key == ord('-') or key == ord('_'):
                        self.display.zoom_out()
                        print("🔍 Thu nhỏ:", self.display.zoom_level)
                    elif key == ord(' '):
                        self.display.scroll_down()
                        print("⬇️ Cuộn xuống")
                    else:
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
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Chế độ demo (không dùng camera)"
    )
    
    args = parser.parse_args()
    
    app = GestureControlledDisplay(
        config_path=args.config,
        camera_id=args.camera,
        headless=args.headless,
        demo=args.demo
    )
    
    app.run()


if __name__ == "__main__":
    main()