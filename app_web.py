"""
Web version - Bảng thông tin công cộng trên trình duyệt
Chạy với Flask để hiển thị trên web
"""

# Cấu hình UTF-8 encoding cho Windows
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from flask import Flask, render_template, jsonify, request, send_file
import cv2
import numpy as np
from pathlib import Path
from data_manager import DataManager
from gui import DisplayGUI, Page
from config import Config
from gesture import GestureRecognizer, GestureType
import io
import base64
import threading
import time

app = Flask(__name__)

# Global camera object - reuse instead of opening/closing repeatedly
camera_cap = None
camera_lock = threading.Lock()

def get_camera():
    """Get or create global camera object"""
    global camera_cap
    try:
        if camera_cap is None:
            print("📷 Initializing camera...")
            camera_cap = cv2.VideoCapture(0)
            camera_cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            # Test if camera works
            ret, frame = camera_cap.read()
            if not ret:
                camera_cap.release()
                camera_cap = None
                print("❌ Camera test failed")
                return None
            print("✓ Camera initialized successfully")
        return camera_cap
    except Exception as e:
        print(f"❌ Camera init error: {e}")
        return None

# Khởi tạo ứng dụng
config = Config.load()
data_manager = DataManager(config.data_dir)
display = DisplayGUI(
    width=config.display_width,
    height=config.display_height,
    font_scale=config.font_scale
)

# Khởi tạo gesture recognizer (lazy - sẽ tạo khi cần)
gesture_recognizer = None

def get_gesture_recognizer():
    """Lấy hoặc tạo gesture recognizer"""
    global gesture_recognizer
    if gesture_recognizer is None:
        print("🔧 Khởi tạo GestureRecognizer...")
        gesture_recognizer = GestureRecognizer(
            min_detection_confidence=config.min_detection_confidence,
            min_tracking_confidence=config.min_tracking_confidence
        )
    return gesture_recognizer

def warmup_gesture_recognizer():
    """Warm up gesture recognizer bằng một frame dummy"""
    try:
        print("🔥 Warming up gesture recognizer...")
        gr = get_gesture_recognizer()
        
        # Tạo frame dummy
        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Process frame dummy vài lần để warm up
        for i in range(3):
            gr.process_frame(dummy_frame)
            time.sleep(0.1)
        
        print("✓ Gesture recognizer warmed up successfully")
        return True
    except Exception as e:
        print(f"⚠ Warmup failed: {e}")
        return False

# Tải nội dung
pages = data_manager.load_pages()
for page in pages:
    display.add_page(page)

# State
current_page = 0
zoom_level = 1.0
scroll_offset = 0
last_gesture = None
last_gesture_time = 0
gesture_cooldown = 0.5  # Cooldown để tránh gesture liên tục


@app.route('/')
def index():
    """Trang chính"""
    return render_template('index.html', 
                          total_pages=display.get_page_count(),
                          current_page=display.get_current_page_index())


@app.route('/gesture-result')
def gesture_result():
    """Trang kết quả nhận diện cử chỉ"""
    return render_template('gesture_result.html')


@app.route('/api/render')
def api_render():
    """API - Render khung hình hiện tại"""
    try:
        frame = display.render(show_debug=False, last_gesture=None)
        
        # Encode frame thành JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        frame_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'success': True,
            'image': f'data:image/jpeg;base64,{frame_base64}',
            'current_page': display.get_current_page_index() + 1,
            'total_pages': display.get_page_count(),
            'zoom_level': f'{display.zoom_level:.1f}x'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/action/<action>', methods=['POST'])
def api_action(action):
    """API - Xử lý hành động"""
    try:
        if action == 'next_page':
            display.next_page()
        elif action == 'prev_page':
            display.previous_page()
        elif action == 'zoom_in':
            display.zoom_in()
        elif action == 'zoom_out':
            display.zoom_out()
        elif action == 'scroll_up':
            display.scroll_up()
        elif action == 'scroll_down':
            display.scroll_down()
        elif action == 'reset':
            display.reset_view()
        else:
            return jsonify({'success': False, 'error': 'Unknown action'})
        
        return jsonify({
            'success': True,
            'current_page': display.get_current_page_index() + 1,
            'total_pages': display.get_page_count(),
            'zoom_level': f'{display.zoom_level:.1f}x'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/camera-frame', methods=['GET'])
def api_camera_frame():
    """API - Trả về frame camera hiện tại (cho hiển thị live feed)"""
    try:
        with camera_lock:
            cap = get_camera()
            if cap is None:
                print("⚠ Camera not available")
                return jsonify({'success': False, 'error': 'Camera not available'})
            
            # Read frame
            ret, frame = cap.read()
            
            if not ret or frame is None:
                print("⚠ Failed to read frame")
                return jsonify({'success': False, 'error': 'Failed to read frame'})
            
            # Resize frame để faster processing
            frame = cv2.resize(frame, (640, 480))
            
            # Encode frame thành JPEG
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            
            print(f"✓ Frame sent: {frame.shape}")
            return jsonify({
                'success': True,
                'frame': frame_base64
            })
    except Exception as e:
        print(f"❌ Camera frame error: {e}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/gesture', methods=['POST'])
def api_gesture():
    """API - Phát hiện cử chỉ từ frame camera"""
    global last_gesture, last_gesture_time
    
    try:
        # Lấy frame từ camera
        with camera_lock:
            cap = get_camera()
            if cap is None:
                print("⚠ Camera not available")
                return jsonify({
                    'success': True, 
                    'gesture': 'none',
                    'confidence': 0,
                    'num_hands': 0,
                    'action': None
                })
            
            print("📷 Capturing frame from camera...")
            ret, frame = cap.read()
            
            if not ret or frame is None:
                print("⚠ Camera capture failed")
                return jsonify({
                    'success': True, 
                    'gesture': 'none',
                    'confidence': 0,
                    'num_hands': 0,
                    'action': None
                })
        
        print(f"✓ Camera frame captured: {frame.shape}")
        
        # Ensure frame is writable
        if not frame.flags.writeable:
            frame = frame.copy()
        
        # Phát hiện gesture
        try:
            gr = get_gesture_recognizer()
            gesture_frame = gr.process_frame(frame)
            gesture = gesture_frame.gesture
            confidence = gesture_frame.confidence
            num_hands = gesture_frame.num_hands
            
            # Log gesture detection
            if num_hands > 0:
                print(f"✓ Detected: {num_hands} hand(s) | Gesture: {gesture.value} | Conf: {confidence:.2f}", flush=True)
            
        except Exception as e:
            print(f"⚠ Gesture detection error: {e}", flush=True)
            try:
                gr = get_gesture_recognizer()
                gr._init_mediapipe()
            except Exception as e2:
                print(f"⚠ MediaPipe re-init error: {e2}", flush=True)
            return jsonify({
                'success': True, 
                'gesture': 'none',
                'confidence': 0,
                'num_hands': 0,
                'action': None
            })
        
        # Tự động xử lý gesture nếu vượt quá cooldown
        current_time = time.time()
        action_performed = None
        
        if gesture != GestureType.NONE and current_time - last_gesture_time >= gesture_cooldown:
            if gesture == GestureType.SWIPE_RIGHT:
                display.next_page()
                action_performed = 'next_page'
                last_gesture_time = current_time
                print(f"✓ Action: {action_performed}")
            elif gesture == GestureType.SWIPE_LEFT:
                display.previous_page()
                action_performed = 'prev_page'
                last_gesture_time = current_time
                print(f"✓ Action: {action_performed}")
            elif gesture == GestureType.ZOOM_IN:
                display.zoom_in()
                action_performed = 'zoom_in'
                last_gesture_time = current_time
                print(f"✓ Action: {action_performed}")
            elif gesture == GestureType.ZOOM_OUT:
                display.zoom_out()
                action_performed = 'zoom_out'
                last_gesture_time = current_time
                print(f"✓ Action: {action_performed}")
            elif gesture == GestureType.SCROLL_UP:
                display.scroll_up()
                action_performed = 'scroll_up'
                last_gesture_time = current_time
                print(f"✓ Action: {action_performed}")
            elif gesture == GestureType.SCROLL_DOWN:
                display.scroll_down()
                action_performed = 'scroll_down'
                last_gesture_time = current_time
                print(f"✓ Action: {action_performed}")
        
        return jsonify({
            'success': True,
            'gesture': gesture.value,
            'confidence': float(confidence),
            'action': action_performed,
            'current_page': display.get_current_page_index() + 1,
            'total_pages': display.get_page_count(),
            'num_hands': num_hands
        })
    except Exception as e:
        print(f"❌ Gesture API error: {str(e)}")
        return jsonify({
            'success': True, 
            'gesture': 'none',
            'confidence': 0,
            'num_hands': 0,
            'action': None
        })


@app.route('/api/gesture-only', methods=['POST'])
def api_gesture_only():
    """API - Phát hiện cử chỉ KHÔNG thực thi (cho trang mobile)"""
    try:
        # Lấy frame từ camera
        with camera_lock:
            cap = get_camera()
            if cap is None:
                print("⚠ Camera not available")
                return jsonify({
                    'success': True, 
                    'gesture': 'none',
                    'confidence': 0,
                    'num_hands': 0
                })
            
            print("📷 Capturing frame from camera (detection only)...")
            ret, frame = cap.read()
            
            if not ret or frame is None:
                print("⚠ Camera capture failed")
                return jsonify({
                    'success': True, 
                    'gesture': 'none',
                    'confidence': 0,
                    'num_hands': 0
                })
        
        print(f"✓ Camera frame captured: {frame.shape}")
        
        # Ensure frame is writable
        if not frame.flags.writeable:
            frame = frame.copy()
        
        # Phát hiện gesture
        try:
            gr = get_gesture_recognizer()
            gesture_frame = gr.process_frame(frame)
            gesture = gesture_frame.gesture
            confidence = gesture_frame.confidence
            num_hands = gesture_frame.num_hands
            
            # Log gesture detection
            if num_hands > 0:
                print(f"✓ Detected: {num_hands} hand(s) | Gesture: {gesture.value} | Conf: {confidence:.2f}", flush=True)
            
        except Exception as e:
            print(f"⚠ Gesture detection error: {e}", flush=True)
            try:
                gr = get_gesture_recognizer()
                gr._init_mediapipe()
            except Exception as e2:
                print(f"⚠ MediaPipe re-init error: {e2}", flush=True)
            return jsonify({
                'success': True, 
                'gesture': 'none',
                'confidence': 0,
                'num_hands': 0
            })
        
        return jsonify({
            'success': True,
            'gesture': gesture.value,
            'confidence': float(confidence),
            'num_hands': num_hands
        })
    except Exception as e:
        print(f"❌ Gesture Only API error: {str(e)}")
        return jsonify({
            'success': True, 
            'gesture': 'none',
            'confidence': 0,
            'num_hands': 0
        })


@app.route('/api/gesture/reset', methods=['POST'])
def api_gesture_reset():
    """API - Reset gesture recognizer"""
    try:
        print("🔄 Resetting gesture recognizer from API...")
        gr = get_gesture_recognizer()
        if gr.reset():
            return jsonify({
                'success': True,
                'message': 'Gesture recognizer reset successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Reset failed'
            })
    except Exception as e:
        error_msg = f"Gesture reset error: {str(e)}"
        print(f"❌ {error_msg}")
        return jsonify({'success': False, 'error': error_msg})


@app.route('/api/gesture/warmup', methods=['POST'])
def api_gesture_warmup():
    """API - Warm up gesture recognizer"""
    try:
        print("🔥 Warming up gesture recognizer...")
        success = warmup_gesture_recognizer()
        if success:
            return jsonify({
                'success': True,
                'message': 'Gesture recognizer warmed up'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Warmup failed'
            })
    except Exception as e:
        error_msg = f"Gesture warmup error: {str(e)}"
        print(f"❌ {error_msg}")
        return jsonify({'success': False, 'error': error_msg})


@app.route('/api/info')
def api_info():
    """API - Thông tin hệ thống"""
    return jsonify({
        'total_pages': display.get_page_count(),
        'current_page': display.get_current_page_index() + 1,
        'zoom_level': f'{display.zoom_level:.1f}x',
        'width': display.width,
        'height': display.height
    })


if __name__ == '__main__':
    print("=" * 60)
    print("BẢNG THÔNG TIN CÔNG CỘNG - WEB VERSION")
    print("=" * 60)
    print(f"✓ Đã tải {display.get_page_count()} trang")
    print("\nMở trình duyệt và truy cập:")
    print("  http://localhost:5000")
    print("\nHoặc từ máy khác:")
    print("  http://<IP_ADDRESS>:5000")
    print("=" * 60)
    
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)
