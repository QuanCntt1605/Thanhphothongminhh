"""
Phụ lục: Các hàm tiện ích bổ sung
"""

import cv2
import numpy as np
from typing import Tuple


def draw_circle_dot(frame: np.ndarray, 
                    x: int, 
                    y: int, 
                    radius: int = 5,
                    color: Tuple[int, int, int] = (0, 255, 0),
                    thickness: int = -1):
    """Vẽ một chấm trên frame"""
    cv2.circle(frame, (x, y), radius, color, thickness)
    return frame


def draw_line(frame: np.ndarray,
              pt1: Tuple[int, int],
              pt2: Tuple[int, int],
              color: Tuple[int, int, int] = (0, 255, 255),
              thickness: int = 2):
    """Vẽ một đường"""
    cv2.line(frame, pt1, pt2, color, thickness)
    return frame


def draw_rectangle(frame: np.ndarray,
                   x: int,
                   y: int,
                   w: int,
                   h: int,
                   color: Tuple[int, int, int] = (255, 0, 0),
                   thickness: int = 2):
    """Vẽ hình chữ nhật"""
    cv2.rectangle(frame, (x, y), (x + w, y + h), color, thickness)
    return frame


def put_text(frame: np.ndarray,
             text: str,
             x: int,
             y: int,
             font_scale: float = 1.0,
             color: Tuple[int, int, int] = (255, 255, 255),
             thickness: int = 2):
    """Vẽ text trên frame"""
    cv2.putText(frame, text, (x, y),
               cv2.FONT_HERSHEY_SIMPLEX,
               font_scale, color, thickness)
    return frame


def resize_image(image: np.ndarray,
                 width: int = None,
                 height: int = None,
                 keep_aspect: bool = True) -> np.ndarray:
    """
    Resize ảnh
    
    Args:
        image: Ảnh gốc
        width: Chiều rộng mới
        height: Chiều cao mới
        keep_aspect: Giữ tỉ lệ
    """
    h, w = image.shape[:2]
    
    if keep_aspect:
        if width is None and height is not None:
            ratio = height / h
            width = int(w * ratio)
        elif height is None and width is not None:
            ratio = width / w
            height = int(h * ratio)
        elif width is not None and height is not None:
            # Tính tỉ lệ nhỏ hơn
            ratio = min(width / w, height / h)
            width = int(w * ratio)
            height = int(h * ratio)
    
    if width and height:
        return cv2.resize(image, (width, height))
    
    return image


def convert_color(frame: np.ndarray, 
                  from_color: str = 'BGR',
                  to_color: str = 'RGB') -> np.ndarray:
    """
    Chuyển đổi màu
    
    Args:
        frame: Ảnh input
        from_color: Màu gốc (BGR, RGB, GRAY, HSV, etc)
        to_color: Màu đích
    """
    color_map = {
        'BGR_RGB': cv2.COLOR_BGR2RGB,
        'RGB_BGR': cv2.COLOR_RGB2BGR,
        'BGR_GRAY': cv2.COLOR_BGR2GRAY,
        'RGB_GRAY': cv2.COLOR_RGB2GRAY,
        'BGR_HSV': cv2.COLOR_BGR2HSV,
        'RGB_HSV': cv2.COLOR_RGB2HSV,
    }
    
    key = f"{from_color}_{to_color}"
    if key in color_map:
        return cv2.cvtColor(frame, color_map[key])
    
    return frame


def get_frame_info(frame: np.ndarray) -> dict:
    """Lấy thông tin frame"""
    h, w = frame.shape[:2]
    channels = frame.shape[2] if len(frame.shape) > 2 else 1
    dtype = frame.dtype
    
    return {
        'width': w,
        'height': h,
        'channels': channels,
        'dtype': str(dtype),
        'resolution': f"{w}x{h}",
        'size_mb': frame.nbytes / 1024 / 1024
    }


def fps_counter(prev_frame_time: float, 
                curr_frame_time: float) -> Tuple[float, str]:
    """
    Tính FPS
    
    Returns:
        (fps, fps_text)
    """
    if curr_frame_time == 0 or prev_frame_time == 0:
        return 0, "FPS: 0"
    
    fps = 1 / (curr_frame_time - prev_frame_time)
    return fps, f"FPS: {fps:.1f}"
