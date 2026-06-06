"""
Module nhận diện cử chỉ tay - OpenCV Skin Detection Version
MediaPipe 0.10+ yêu cầu TensorFlow -> NumPy 2.x incompatibility issue
Dùng OpenCV skin detection + motion history để phát hiện cử chỉ
"""

import os
import warnings
warnings.filterwarnings('ignore')

import cv2
import numpy as np
import time
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Tuple, List


class GestureType(Enum):
    """Các loại cử chỉ được hỗ trợ"""
    NONE = "none"
    SWIPE_LEFT = "swipe_left"
    SWIPE_RIGHT = "swipe_right"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"
    SCROLL_UP = "scroll_up"
    SCROLL_DOWN = "scroll_down"
    PAUSE = "pause"
    GRAB = "grab"


@dataclass
class GestureFrame:
    """Chứa thông tin khung hình và cử chỉ"""
    frame: np.ndarray
    gesture: GestureType
    confidence: float
    hand_landmarks: Optional[list] = None
    num_hands: int = 0


class GestureRecognizer:
    """Nhận diện cử chỉ dùng OpenCV skin detection + motion tracking"""
    
    def __init__(self, 
                 min_detection_confidence: float = 0.6,
                 min_tracking_confidence: float = 0.5):
        """Khởi tạo GestureRecognizer"""
        print("🔧 Khởi tạo GestureRecognizer (OpenCV Skin Detection Mode)")
        
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        self.frames_processed = 0
        
        # Motion history
        self.hand_centers = []
        self.max_history = 15
        self.swipe_threshold = 20
        self.last_frame = None
        
    def _detect_skin(self, frame: np.ndarray) -> np.ndarray:
        """Detect skin regions using HSV color space"""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Skin color range in HSV (lower and upper bounds)
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        
        # Additional skin tone range
        lower_skin2 = np.array([170, 20, 70], dtype=np.uint8)
        upper_skin2 = np.array([180, 255, 255], dtype=np.uint8)
        
        # Create mask
        mask1 = cv2.inRange(hsv, lower_skin, upper_skin)
        mask2 = cv2.inRange(hsv, lower_skin2, upper_skin2)
        mask = cv2.bitwise_or(mask1, mask2)
        
        # Apply morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        return mask
    
    def _find_hand_centers(self, mask: np.ndarray) -> List[Tuple[int, int]]:
        """Find hand center positions from mask"""
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        centers = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            # Filter by size - hand should have reasonable area
            if 500 < area < 50000:
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    centers.append((cx, cy))
        
        return centers[:2]  # Max 2 hands
    
    def _detect_swipe(self) -> Optional[GestureType]:
        """Detect swipe gesture from motion history"""
        if len(self.hand_centers) < 5:
            return None
        
        start = self.hand_centers[0]
        end = self.hand_centers[-1]
        
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        
        distance = np.sqrt(dx**2 + dy**2)
        if distance < self.swipe_threshold:
            return None
        
        # Determine direction
        if abs(dx) > abs(dy):  # Horizontal swipe
            if dx > 0:
                return GestureType.SWIPE_RIGHT
            else:
                return GestureType.SWIPE_LEFT
        else:  # Vertical swipe
            if dy > 0:
                return GestureType.SCROLL_DOWN
            else:
                return GestureType.SCROLL_UP
        
        return None
    
    def process_frame(self, frame: np.ndarray) -> GestureFrame:
        """
        Xử lý frame và phát hiện cử chỉ
        
        Args:
            frame: Khung hình BGR từ camera
            
        Returns:
            GestureFrame với cử chỉ được phát hiện
        """
        self.frames_processed += 1
        h, w = frame.shape[:2]
        
        # Detect skin
        mask = self._detect_skin(frame)
        
        # Find hand centers
        centers = self._find_hand_centers(mask)
        num_hands = len(centers)
        
        # Update history
        if num_hands > 0:
            self.hand_centers.extend(centers)
            if len(self.hand_centers) > self.max_history:
                self.hand_centers = self.hand_centers[-self.max_history:]
        else:
            self.hand_centers.clear()
        
        # Detect gesture
        gesture = GestureType.NONE
        confidence = 0.0
        
        if num_hands > 0 and len(self.hand_centers) >= 5:
            detected_gesture = self._detect_swipe()
            if detected_gesture:
                gesture = detected_gesture
                confidence = 0.7
                print(f"✓ Gesture detected: {gesture.value} (confidence: {confidence:.2f})")
        
        self.last_frame = frame.copy()
        
        return GestureFrame(
            frame=frame,
            gesture=gesture,
            confidence=confidence,
            hand_landmarks=None,
            num_hands=num_hands
        )
    
    def reset(self):
        """Reset gesture recognizer"""
        print("🔄 Resetting gesture recognizer...")
        self.hand_centers.clear()
        self.last_frame = None
        return True
