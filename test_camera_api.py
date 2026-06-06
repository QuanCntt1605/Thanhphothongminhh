import requests
import json

try:
    response = requests.get('http://localhost:5000/api/camera-frame', timeout=3)
    if response.status_code == 200:
        data = response.json()
        success = data.get('success')
        frame_size = len(data.get('frame', ''))
        print(f'✓ Camera endpoint OK')
        print(f'  - success: {success}')
        print(f'  - frame size: {frame_size} bytes')
    else:
        print(f'✗ Camera error: {response.status_code}')
except Exception as e:
    print(f'✗ Error: {e}')
