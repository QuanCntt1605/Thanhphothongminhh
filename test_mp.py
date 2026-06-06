#!/usr/bin/env python
import mediapipe as mp

print('✓ MediaPipe version:', mp.__version__)
print('✓ Has solutions:', hasattr(mp, 'solutions'))

from mediapipe import solutions
print('✓ Solutions imported')

hands = solutions.hands
print('✓ Hands imported')

hand_detector = hands.Hands()
print('✓ Hands object created successfully')

import numpy as np
dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
results = hand_detector.process(dummy_frame)
print('✓ Frame processed')
print('✓ All tests passed!')
