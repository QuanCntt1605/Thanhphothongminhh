"""
Module nhận diện cử chỉ tay sử dụng MediaPipe
Hỗ trợ các cử chỉ: vuốt sang, zoom, cữu cuộn
"""

import cv2
import numpy as np
import mediapipe as mp
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Tuple

# MediaPipe initialization
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils


class GestureType(Enum):
    """Các loại cử chỉ được hỗ trợ"""
    NONE = "none"
    SWIPE_LEFT = "swipe_left"       # Vuốt trái
    SWIPE_RIGHT = "swipe_right"     # Vuốt phải
    ZOOM_IN = "zoom_in"             # Thu nhỏ
    ZOOM_OUT = "zoom_out"           # Phóng to
    SCROLL_UP = "scroll_up"         # Cuộn lên
    SCROLL_DOWN = "scroll_down"     # Cuộn xuống
    PAUSE = "pause"                 # Dừng
    GRAB = "grab"                   # Nắm tay


@dataclass
class GestureFrame:
    """Chứa thông tin khung hình và cử chỉ"""
    frame: np.ndarray
    gesture: GestureType
    confidence: float
    hand_landmarks: Optional[list] = None
    num_hands: int = 0


class GestureRecognizer:
    """Nhận diện cử chỉ từ video stream"""
    
    def __init__(self, 
                 min_detection_confidence: float = 0.5,
                 min_tracking_confidence: float = 0.5):
        """
        Khởi tạo GestureRecognizer
        
        Args:
            min_detection_confidence: Độ tin cậy phát hiện tối thiểu
            min_tracking_confidence: Độ tin cậy theo dõi tối thiểu
        """
        self.hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        
        # Lịch sử vị trí để phát hiện vuốt
        self.hand_history = {
            0: [],  # Tay phải
            1: []   # Tay trái
        }
        self.history_max_length = 30
        self.swipe_threshold = 50  # Pixel
        
        # Để đo khoảng cách ngón cho zoom
        self.previous_distance = None
        self.zoom_threshold = 20  # Pixel
        
    def get_hand_center(self, landmarks) -> Tuple[int, int]:
        """Tính trung tâm của bàn tay từ các điểm landmark"""
        x_coords = [lm.x for lm in landmarks]
        y_coords = [lm.y for lm in landmarks]
        
        center_x = int(np.mean(x_coords) * 1280)  # Giả sử độ rộng 1280
        center_y = int(np.mean(y_coords) * 720)   # Giả sử độ cao 720
        
        return center_x, center_y
    
    def get_distance(self, point1, point2) -> float:
        """Tính khoảng cách Euclidean giữa hai điểm"""
        return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    def detect_swipe(self, hand_id: int) -> Optional[GestureType]:
        """Phát hiện cử chỉ vuốt"""
        history = self.hand_history[hand_id]
        
        if len(history) < 10:
            return None
        
        # So sánh vị trí đầu và cuối
        start_pos = history[0]
        end_pos = history[-1]
        
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        
        # Vuốt sang phải
        if dx > self.swipe_threshold and abs(dy) < self.swipe_threshold:
            return GestureType.SWIPE_RIGHT
        
        # Vuốt sang trái
        if dx < -self.swipe_threshold and abs(dy) < self.swipe_threshold:
            return GestureType.SWIPE_LEFT
        
        # Cuộn lên
        if dy < -self.swipe_threshold and abs(dx) < self.swipe_threshold:
            return GestureType.SCROLL_UP
        
        # Cuộn xuống
        if dy > self.swipe_threshold and abs(dx) < self.swipe_threshold:
            return GestureType.SCROLL_DOWN
        
        return None
    
    def detect_zoom(self, landmarks_list: list) -> Optional[GestureType]:
        """Phát hiện cử chỉ zoom (khoảng cách giữa hai tay)"""
        if len(landmarks_list) < 2:
            return None
        
        # Lấy vị trí ngón trỏ của hai tay
        hand1_index = landmarks_list[0][8]  # Ngón trỏ tay 1
        hand2_index = landmarks_list[1][8]  # Ngón trỏ tay 2
        
        point1 = (int(hand1_index.x * 1280), int(hand1_index.y * 720))
        point2 = (int(hand2_index.x * 1280), int(hand2_index.y * 720))
        
        distance = self.get_distance(point1, point2)
        
        if self.previous_distance is not None:
            distance_diff = distance - self.previous_distance
            
            # Khoảng cách tăng -> zoom out
            if distance_diff > self.zoom_threshold:
                self.previous_distance = distance
                return GestureType.ZOOM_OUT
            
            # Khoảng cách giảm -> zoom in
            if distance_diff < -self.zoom_threshold:
                self.previous_distance = distance
                return GestureType.ZOOM_IN
        
        self.previous_distance = distance
        return None
    
    def is_fist(self, landmarks) -> bool:
        """Kiểm tra xem bàn tay có phải là nắm tay (grab) không"""
        # Nếu tất cả các ngón đều gập lại
        fingers = [
            landmarks[4],   # Ngón cái
            landmarks[8],   # Ngón trỏ
            landmarks[12],  # Ngón giữa
            landmarks[16],  # Ngón áp út
            landmarks[20]   # Ngón út
        ]
        
        # Kiểm tra nếu các ngón đều dưới các khớp (landmarks chỉ có 21 điểm)
        palm_y = landmarks[0].y
        extended_fingers = sum(1 for f in fingers if f.y < palm_y)
        
        return extended_fingers < 2
    
    def process_frame(self, frame: np.ndarray) -> GestureFrame:
        """
        Xử lý một khung hình và phát hiện cử chỉ
        
        Args:
            frame: Khung hình BGR từ camera
            
        Returns:
            GestureFrame với cử chỉ được phát hiện
        """
        h, w, c = frame.shape
        
        # Chuyển sang RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)
        
        gesture = GestureType.NONE
        confidence = 0.0
        num_hands = 0
        landmarks_list = []
        
        if results.multi_hand_landmarks:
            num_hands = len(results.multi_hand_landmarks)
            landmarks_list = results.multi_hand_landmarks
            
            # Xử lý từng bàn tay
            for hand_id, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # Cập nhật lịch sử vị trí
                center = self.get_hand_center(hand_landmarks)
                self.hand_history[hand_id].append(center)
                
                # Giữ lịch sử chỉ có số phần tử tối đa
                if len(self.hand_history[hand_id]) > self.history_max_length:
                    self.hand_history[hand_id].pop(0)
                
                # Phát hiện vuốt
                swipe = self.detect_swipe(hand_id)
                if swipe:
                    gesture = swipe
                    confidence = 0.9
                
                # Phát hiện nắm tay
                if self.is_fist(hand_landmarks.landmark):
                    gesture = GestureType.GRAB
                    confidence = 0.85
            
            # Phát hiện zoom (nếu có 2 tay)
            if num_hands >= 2:
                zoom_gesture = self.detect_zoom(landmarks_list)
                if zoom_gesture:
                    gesture = zoom_gesture
                    confidence = 0.8
        else:
            # Xóa lịch sử khi không có tay
            self.hand_history[0].clear()
            self.hand_history[1].clear()
            self.previous_distance = None
        
        return GestureFrame(
            frame=frame,
            gesture=gesture,
            confidence=confidence,
            hand_landmarks=landmarks_list,
            num_hands=num_hands
        )
    
    def draw_landmarks(self, frame: np.ndarray, 
                       gesture_frame: GestureFrame) -> np.ndarray:
        """Vẽ landmarks trên khung hình"""
        if gesture_frame.hand_landmarks:
            for hand_landmarks in gesture_frame.hand_landmarks:
                mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS
                )
        
        return frame
