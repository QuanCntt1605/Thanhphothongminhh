"""
Module giao diện bảng thông tin công cộng - Nâng cấp
Hiển thị nội dung, hỗ trợ phân trang, zoom, cuộn
Hỗ trợ tiếng Việt UTF-8 đúng cách bằng PIL
"""

import cv2
import numpy as np
from typing import List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from PIL import Image, ImageDraw, ImageFont
import os


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
    background_color: Tuple[int, int, int] = (255, 255, 255)  # Trắng


class DisplayGUI:
    """Giao diện hiển thị bảng thông tin - Nâng cấp"""
    
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
        
        # Font cho tiếng Việt - sử dụng font system
        self.load_fonts()
        
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
        self.line_height = 45
        
        # Màu sắc - Giao diện hiện đại (Nền trắng)
        self.bg_color = (255, 255, 255)        # Trắng
        self.bg_color_rgb = (255, 255, 255)    # RGB Trắng
        self.text_color = (0, 0, 0)            # Đen
        self.title_color = (0, 100, 200)       # Xanh đậm
        self.accent_color = (0, 150, 100)      # Xanh lá
        self.highlight_color = (200, 50, 50)   # Đỏ đậm
        
        # Thêm màu sắc mới cho giao diện nâng cấp (Nền trắng)
        self.primary_color = (0, 100, 200)      # Xanh biển đậm
        self.secondary_color = (0, 150, 100)    # Xanh lá
        self.danger_color = (200, 50, 100)      # Đỏ
        self.success_color = (50, 150, 50)      # Xanh lá sáng
        self.warning_color = (200, 120, 0)      # Cam
        self.dark_bg = (255, 255, 255)          # Nền trắng
        self.card_bg = (240, 245, 250)          # Nền card xám nhạt
        
        # Hiệu ứng và animation
        self.animation_frame = 0
        self.show_gesture_indicator = False
        self.gesture_indicator_time = 0
    
    def load_fonts(self):
        """Load font hỗ trợ tiếng Việt"""
        # Tìm font có sẵn trong hệ thống
        font_paths = [
            "C:\\Windows\\Fonts\\arial.ttf",
            "C:\\Windows\\Fonts\\tahoma.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/System/Library/Fonts/Arial.ttf"
        ]
        
        self.font_large = None
        self.font_normal = None
        self.font_small = None
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    self.font_large = ImageFont.truetype(font_path, 36)
                    self.font_normal = ImageFont.truetype(font_path, 24)
                    self.font_small = ImageFont.truetype(font_path, 18)
                    break
                except:
                    continue
        
        # Fallback to default font nếu không tìm được
        if self.font_large is None:
            self.font_large = ImageFont.load_default()
            self.font_normal = ImageFont.load_default()
            self.font_small = ImageFont.load_default()
    
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
        self.scroll_offset = max(0, self.scroll_offset - int(self.line_height * 1.5))
    
    def scroll_down(self):
        """Cuộn xuống"""
        if len(self.pages) > 0:
            page = self.pages[self.current_page]
            lines = page.content.split('\n')
            max_offset = len(lines) * self.line_height
            self.scroll_offset = min(self.scroll_offset + int(self.line_height * 1.5), max_offset)
    
    def reset_view(self):
        """Đặt lại view về mặc định"""
        self.scroll_offset = 0
        self.zoom_level = 1.0
    
    def _cv2_to_pil(self, cv_img: np.ndarray) -> Image.Image:
        """Chuyển đổi từ OpenCV BGR sang PIL RGB"""
        rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        return Image.fromarray(rgb)
    
    def _pil_to_cv2(self, pil_img: Image.Image) -> np.ndarray:
        """Chuyển đổi từ PIL RGB sang OpenCV BGR"""
        rgb = np.array(pil_img)
        return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    
    def render(self, show_debug: bool = False, last_gesture=None) -> np.ndarray:
        """
        Render khung hình hiển thị với UI nâng cấp
        
        Args:
            show_debug: Hiển thị thông tin debug
            last_gesture: Cử chỉ cuối cùng được phát hiện
            
        Returns:
            Khung hình BGR
        """
        # Tạo hình PIL với gradient nền
        pil_image = Image.new('RGB', (self.width, self.height), self.dark_bg)
        draw = ImageDraw.Draw(pil_image)
        
        # Vẽ gradient nền (từ tối đến sáng)
        self._draw_gradient_background(pil_image)
        
        if len(self.pages) == 0:
            # Hiển thị thông báo nếu không có trang
            self._draw_empty_state(pil_image, draw)
            return self._pil_to_cv2(pil_image)
        
        page = self.pages[self.current_page]
        
        # === HEADER / TIÊU ĐỀ ===
        self._draw_header(pil_image, draw, page)
        
        # === NỘI DUNG CHÍNH ===
        self._draw_content(pil_image, draw, page)
        
        # === FOOTER ===
        self._draw_footer(pil_image, draw, last_gesture, show_debug)
        
        # === GESTURE INDICATOR ===
        if last_gesture:
            self._draw_gesture_indicator(pil_image, draw, last_gesture)
        
        # Chuyển đổi PIL thành OpenCV
        frame = self._pil_to_cv2(pil_image)
        self.animation_frame += 1
        
        return frame
    
    def _draw_gradient_background(self, pil_image: Image.Image):
        """Vẽ nền trắng hoặc gradient nhạt"""
        gradient = Image.new('RGB', (self.width, self.height))
        gradient_data = gradient.load()
        
        for y in range(self.height):
            # Tạo gradient từ trắng sang xám nhạt
            ratio = y / self.height
            r = int(255 - (10 * ratio))   # 255 -> 245
            g = int(255 - (10 * ratio))   # 255 -> 245
            b = int(255 - (5 * ratio))    # 255 -> 250
            
            for x in range(self.width):
                gradient_data[x, y] = (r, g, b)
        
        # Paste gradient directly without mask
        pil_image.paste(gradient, (0, 0))
    
    def _draw_empty_state(self, pil_image: Image.Image, draw):
        """Hiển thị trạng thái trống"""
        text = "Không có dữ liệu"
        bbox = draw.textbbox((0, 0), text, font=self.font_large)
        text_width = bbox[2] - bbox[0]
        
        x = (self.width - text_width) // 2
        y = self.height // 2 - 50
        
        # Vẽ text với hiệu ứng shadow
        draw.text((x + 2, y + 2), text, fill=(200, 200, 200), font=self.font_large)
        draw.text((x, y), text, fill=self.primary_color, font=self.font_large)
    
    def _draw_header(self, pil_image: Image.Image, draw, page: Page):
        """Vẽ header với tiêu đề"""
        title_height = 100
        
        # Vẽ header background với màu nhạt
        header_img = Image.new('RGB', (self.width, title_height), (245, 248, 250))
        pil_image.paste(header_img, (0, 0))
        
        # Vẽ đường trang trí trên và dưới
        draw.rectangle([(0, 0), (self.width, 2)], fill=self.primary_color)
        draw.rectangle([(0, title_height - 4), (self.width, title_height)], 
                      fill=self.primary_color)
        
        # Vẽ icon/hình trang trí bên trái
        draw.rectangle([(20, 30), (40, 70)], fill=self.primary_color)
        
        # Vẽ tiêu đề với hiệu ứng shadow
        title_x = 60
        title_y = 32
        
        # Shadow
        draw.text((title_x + 2, title_y + 2), page.title, 
                 fill=(200, 200, 200), font=self.font_large)
        # Main text
        draw.text((title_x, title_y), page.title, 
                 fill=self.primary_color, font=self.font_large)
    
    def _draw_content(self, pil_image: Image.Image, draw, page: Page):
        """Vẽ nội dung chính"""
        content_y = 120
        content_height = self.height - 150
        
        # Áp dụng scroll offset
        display_y = content_y - self.scroll_offset
        
        # Áp dụng zoom
        font_size_zoomed = max(16, int(24 * self.zoom_level))
        try:
            font_zoomed = ImageFont.truetype(
                "C:\\Windows\\Fonts\\arial.ttf", font_size_zoomed
            )
        except:
            font_zoomed = self.font_normal
        
        # Vẽ hình ảnh nếu có
        if page.images and len(page.images) > 0:
            display_y = self._draw_image_card(pil_image, draw, page.images[0], 
                                            display_y, font_size_zoomed)
        
        # Vẽ nội dung text
        text_x = 60
        text_lines = page.content.split('\n')
        
        for line in text_lines:
            if display_y > self.height - 120:
                break
            
            if line.strip():
                # Bọc text nếu quá dài
                wrapped_lines = self._wrap_text(line, font_zoomed, self.width - 120)
                for wrapped_line in wrapped_lines:
                    if display_y > self.height - 120:
                        break
                    
                    # Vẽ background cho dòng (card effect)
                    if len(wrapped_line.strip()) > 30:
                        draw.rectangle(
                            [(50, int(display_y) - 5), 
                             (self.width - 50, int(display_y) + 30)],
                            fill=(240, 245, 250),
                            outline=self.primary_color
                        )
                    
                    # Hiệu ứng text với shadow nhạt
                    draw.text((text_x + 1, int(display_y) + 1), wrapped_line, 
                             fill=(200, 200, 200), font=font_zoomed)  # Shadow
                    draw.text((text_x, int(display_y)), wrapped_line, 
                             fill=(0, 0, 0), font=font_zoomed)  # Dark text
                    display_y += int(self.line_height * self.zoom_level)
            else:
                display_y += int(self.line_height * 0.5)
    
    def _draw_image_card(self, pil_image: Image.Image, draw, 
                        img: np.ndarray, y_pos: float, font_size: int) -> float:
        """Vẽ hình ảnh với card effect"""
        img_h = int(img.shape[0] * self.zoom_level * 0.5)
        img_w = int(img.shape[1] * self.zoom_level * 0.5)
        
        if img_h > 0 and img_w > 0:
            img_resized = cv2.resize(img, (img_w, img_h))
            pil_img = self._cv2_to_pil(img_resized)
            
            # Thêm border và shadow cho hình ảnh
            card_w = img_w + 20
            card_h = img_h + 20
            
            # Shadow
            shadow_img = Image.new('RGB', (card_w + 5, card_h + 5), (200, 200, 200))
            x_offset = (self.width - card_w) // 2
            pil_image.paste(shadow_img, (x_offset + 5, int(y_pos) + 5), shadow_img)
            
            # Card background - nhạt hơn
            card_img = Image.new('RGB', (card_w, card_h), (245, 248, 250))
            card_draw = ImageDraw.Draw(card_img)
            card_draw.rectangle([(0, 0), (card_w - 1, card_h - 1)], 
                               outline=self.primary_color, width=2)
            card_img.paste(pil_img, (10, 10))
            
            pil_image.paste(card_img, (x_offset, int(y_pos)))
            return y_pos + card_h + 30
        
        return y_pos
    
    def _draw_footer(self, pil_image: Image.Image, draw, last_gesture=None, 
                    show_debug: bool = False):
        """Vẽ footer"""
        footer_y = self.height - 60
        
        # Vẽ đường trang trí
        draw.rectangle([(0, footer_y - 5), (self.width, footer_y - 2)],
                      fill=self.primary_color)
        
        # Thông tin trang
        page_text = f"Trang {self.current_page + 1}/{len(self.pages)}"
        draw.text((60, footer_y + 8), page_text, 
                 fill=self.primary_color, font=self.font_normal)
        
        # Zoom level
        zoom_text = f"Zoom: {self.zoom_level:.1f}x"
        draw.text((self.width - 300, footer_y + 8), zoom_text, 
                 fill=self.primary_color, font=self.font_normal)
        
        # Hướng dẫn
        hint_text = "Vuốt/Cuộn: Điều hướng | Thu/Phóng: Thay đổi kích thước"
        bbox = draw.textbbox((0, 0), hint_text, font=self.font_small)
        text_width = bbox[2] - bbox[0]
        hint_x = (self.width - text_width) // 2
        draw.text((hint_x, footer_y + 15), hint_text, 
                 fill=(100, 100, 100), font=self.font_small)
        
        # Debug info
        if show_debug:
            debug_y = 20
            debug_texts = [
                f"Pages: {len(self.pages)}",
                f"Current: {self.current_page}",
                f"Zoom: {self.zoom_level:.2f}",
                f"Scroll: {self.scroll_offset}",
            ]
            for debug_text in debug_texts:
                draw.text((self.width - 300, debug_y), debug_text, 
                         fill=(200, 200, 100), font=self.font_small)
                debug_y += 25
    
    def _draw_gesture_indicator(self, pil_image: Image.Image, draw, gesture_type):
        """Vẽ chỉ báo cử chỉ"""
        indicator_size = 60
        indicator_x = self.width - indicator_size - 30
        indicator_y = 30
        
        # Chọn màu dựa trên loại gesture
        gesture_colors = {
            "swipe_left": self.warning_color,
            "swipe_right": self.success_color,
            "zoom_in": self.primary_color,
            "zoom_out": self.secondary_color,
            "scroll_up": self.accent_color,
            "scroll_down": self.danger_color,
            "grab": self.highlight_color,
        }
        
        color = gesture_colors.get(gesture_type.value, self.primary_color)
        
        # Vẽ hình tròn với animation
        pulse = abs(np.sin(self.animation_frame * 0.1)) * 10 + 5
        draw.ellipse(
            [(indicator_x - pulse, indicator_y - pulse),
             (indicator_x + indicator_size + pulse, indicator_y + indicator_size + pulse)],
            outline=color,
            width=2
        )
        
        # Vẽ hình tròn cơ bản
        draw.ellipse(
            [(indicator_x, indicator_y),
             (indicator_x + indicator_size, indicator_y + indicator_size)],
            fill=color,
            outline=(0, 0, 0),
            width=2
        )
        
        # Vẽ biểu tượng gesture với text màu trắng
        gesture_icon = self._get_gesture_icon(gesture_type.value)
        draw.text((indicator_x + 10, indicator_y + 10), gesture_icon, 
                 fill=(255, 255, 255), font=self.font_small)
    
    def _get_gesture_icon(self, gesture: str) -> str:
        """Lấy biểu tượng gesture"""
        icons = {
            "swipe_left": "◀",
            "swipe_right": "▶",
            "zoom_in": "+",
            "zoom_out": "-",
            "scroll_up": "▲",
            "scroll_down": "▼",
            "grab": "✊",
        }
        return icons.get(gesture, "?")
    
    def _wrap_text(self, text: str, font, max_width: int) -> List[str]:
        """Bọc text để vừa trong chiều rộng tối đa"""
        if not text:
            return []
        
        words = text.split(' ')
        lines = []
        current_line = ""
        
        draw_temp = ImageDraw.Draw(Image.new('RGB', (1, 1)))
        
        for word in words:
            test_line = f"{current_line} {word}".strip()
            bbox = draw_temp.textbbox((0, 0), test_line, font=font)
            text_width = bbox[2] - bbox[0]
            
            if text_width > max_width:
                if current_line:
                    lines.append(current_line)
                current_line = word
            else:
                current_line = test_line
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def get_page_count(self) -> int:
        """Lấy số lượng trang"""
        return len(self.pages)
    
    def get_current_page_index(self) -> int:
        """Lấy index trang hiện tại"""
        return self.current_page
