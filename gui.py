"""
Module giao diện bảng thông tin công cộng
Hiển thị nội dung, hỗ trợ phân trang, zoom, cuộn
"""

import cv2
import numpy as np
from typing import List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class ContentType(Enum):
    """Loại nội dung"""
    TEXT = "text"
    IMAGE = "image"
    MIXED = "mixed"


@dataclass
class Page:
    """Một trang nội dung"""
    title: str
    content: str
    images: List[np.ndarray] = None
    background_color: Tuple[int, int, int] = (25, 25, 112)  # Midnight Blue


class DisplayGUI:
    """Giao diện hiển thị bảng thông tin"""
    
    def __init__(self, 
                 width: int = 1280,
                 height: int = 720,
                 font_scale: float = 1.0):
        """
        Khởi tạo DisplayGUI
        
        Args:
            width: Chiều rộng màn hình
            height: Chiều cao màn hình
            font_scale: Kích thước font mặc định
        """
        self.width = width
        self.height = height
        self.font_scale = font_scale
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        
        # Nội dung
        self.pages: List[Page] = []
        self.current_page = 0
        
        # Zoom
        self.zoom_level = 1.0
        self.min_zoom = 0.5
        self.max_zoom = 3.0
        self.zoom_step = 0.1
        
        # Cuộn
        self.scroll_offset = 0
        self.line_height = 40
        
        # Màu sắc
        self.bg_color = (25, 25, 112)      # Midnight Blue
        self.text_color = (255, 255, 255)  # Trắng
        self.title_color = (0, 255, 255)   # Cyan
        self.highlight_color = (0, 255, 0) # Xanh
        
    def add_page(self, page: Page):
        """Thêm một trang nội dung"""
        self.pages.append(page)
    
    def next_page(self):
        """Chuyển đến trang tiếp theo"""
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            self.scroll_offset = 0
            self.zoom_level = 1.0
    
    def previous_page(self):
        """Chuyển đến trang trước"""
        if self.current_page > 0:
            self.current_page -= 1
            self.scroll_offset = 0
            self.zoom_level = 1.0
    
    def zoom_in(self):
        """Phóng to"""
        if self.zoom_level < self.max_zoom:
            self.zoom_level += self.zoom_step
    
    def zoom_out(self):
        """Thu nhỏ"""
        if self.zoom_level > self.min_zoom:
            self.zoom_level -= self.zoom_step
    
    def scroll_up(self):
        """Cuộn lên"""
        self.scroll_offset = max(0, self.scroll_offset - self.line_height // 2)
    
    def scroll_down(self):
        """Cuộn xuống"""
        # Tính toán chiều cao tối đa có thể cuộn
        if len(self.pages) > 0:
            page = self.pages[self.current_page]
            # Ước tính số dòng
            lines = page.content.split('\n')
            max_offset = len(lines) * self.line_height
            
            self.scroll_offset = min(self.scroll_offset + self.line_height // 2, max_offset)
    
    def reset_view(self):
        """Đặt lại view về mặc định"""
        self.scroll_offset = 0
        self.zoom_level = 1.0
    
    def _draw_text_wrapped(self, 
                          frame: np.ndarray,
                          text: str,
                          x: int,
                          y: int,
                          font_scale: float,
                          color: Tuple[int, int, int],
                          max_width: int,
                          thickness: int = 2) -> int:
        """
        Vẽ text với tự động xuống dòng
        
        Returns: Chiều cao tổng cộng của text
        """
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = f"{current_line} {word}".strip()
            text_size = cv2.getTextSize(test_line, self.font, font_scale, thickness)[0]
            
            if text_size[0] > max_width:
                if current_line:
                    lines.append(current_line)
                current_line = word
            else:
                current_line = test_line
        
        if current_line:
            lines.append(current_line)
        
        # Vẽ từng dòng
        current_y = y
        for line in lines:
            cv2.putText(frame, line, (x, current_y),
                       self.font, font_scale, color, thickness)
            current_y += int(self.line_height * font_scale)
        
        return current_y - y
    
    def render(self, show_debug: bool = False) -> np.ndarray:
        """
        Render khung hình hiển thị
        
        Args:
            show_debug: Hiển thị thông tin debug
            
        Returns:
            Khung hình BGR
        """
        # Tạo khung nền
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        frame[:] = self.bg_color
        
        if len(self.pages) == 0:
            # Hiển thị thông báo nếu không có trang
            cv2.putText(frame, "Khong co du lieu", (50, self.height // 2),
                       self.font, 1.5, self.text_color, 2)
            return frame
        
        page = self.pages[self.current_page]
        
        # Vẽ tiêu đề
        title_height = 80
        cv2.rectangle(frame, (0, 0), (self.width, title_height), 
                     (40, 40, 80), -1)
        cv2.putText(frame, page.title, (50, 50),
                   self.font, 2, self.title_color, 3)
        
        # Vẽ nội dung chính
        content_y = title_height + 30
        content_height = self.height - title_height - 120
        
        # Áp dụng scroll offset
        display_y = content_y - self.scroll_offset
        
        # Áp dụng zoom
        font_scale_zoomed = self.font_scale * self.zoom_level
        
        # Chia nội dung thành các phần (text + images)
        if page.images:
            # Nếu có hình ảnh, hiển thị hình ảnh đầu tiên
            img = page.images[0]
            img_h = int(img.shape[0] * self.zoom_level)
            img_w = int(img.shape[1] * self.zoom_level)
            
            # Resize ảnh
            if img_h > 0 and img_w > 0:
                img_resized = cv2.resize(img, (img_w, img_h))
                
                # Tính vị trí để căn giữa
                x_offset = (self.width - img_w) // 2
                
                # Vẽ ảnh
                frame[display_y:display_y + img_h, x_offset:x_offset + img_w] = img_resized
                display_y += img_h + 20
        
        # Vẽ text nội dung
        text_x = 50
        text_max_width = self.width - 100
        
        self._draw_text_wrapped(
            frame,
            page.content,
            text_x,
            display_y,
            font_scale_zoomed,
            self.text_color,
            int(text_max_width / self.zoom_level),
            thickness=2
        )
        
        # Vẽ footer với thông tin trang
        footer_y = self.height - 40
        cv2.line(frame, (0, footer_y - 10), (self.width, footer_y - 10),
                self.highlight_color, 2)
        
        # Số trang
        page_text = f"Trang {self.current_page + 1}/{len(self.pages)}"
        cv2.putText(frame, page_text, (50, footer_y),
                   self.font, 0.8, self.highlight_color, 2)
        
        # Mức zoom
        zoom_text = f"Zoom: {self.zoom_level:.1f}x"
        text_size = cv2.getTextSize(zoom_text, self.font, 0.8, 2)[0]
        cv2.putText(frame, zoom_text, (self.width - text_size[0] - 50, footer_y),
                   self.font, 0.8, self.highlight_color, 2)
        
        if show_debug:
            # Hiển thị debug info
            debug_y = 50
            debug_texts = [
                f"Pages: {len(self.pages)}",
                f"Current: {self.current_page}",
                f"Zoom: {self.zoom_level:.2f}",
                f"Scroll: {self.scroll_offset}",
            ]
            for debug_text in debug_texts:
                cv2.putText(frame, debug_text, (self.width - 300, debug_y),
                           self.font, 0.5, (200, 200, 0), 1)
                debug_y += 25
        
        return frame
    
    def get_page_count(self) -> int:
        """Lấy số lượng trang"""
        return len(self.pages)
    
    def get_current_page_index(self) -> int:
        """Lấy index trang hiện tại"""
        return self.current_page
