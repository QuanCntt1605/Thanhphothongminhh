"""
Module quản lý cấu hình hệ thống
Hỗ trợ YAML, JSON, và cấu hình mặc định
"""

import yaml
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Config:
    """Cấu hình hệ thống"""
    
    # Display settings
    display_width: int = 1280
    display_height: int = 720
    font_scale: float = 1.0
    
    # Camera settings
    camera_width: int = 640
    camera_height: int = 480
    camera_fps: int = 30
    camera_preview_width: int = 320
    camera_preview_height: int = 240
    camera_id: int = 0
    
    # MediaPipe settings
    min_detection_confidence: float = 0.5
    min_tracking_confidence: float = 0.5
    max_num_hands: int = 2
    
    # Gesture settings
    swipe_threshold: int = 50      # Pixel
    zoom_threshold: int = 20        # Pixel
    scroll_threshold: int = 30      # Pixel
    
    # Data settings
    data_dir: str = "data"
    
    @classmethod
    def load(cls, config_path: Optional[str] = None) -> 'Config':
        """
        Tải cấu hình từ file hoặc sử dụng giá trị mặc định
        
        Args:
            config_path: Đường dẫn file cấu hình (.yaml hoặc .json)
            
        Returns:
            Config object
        """
        config = cls()
        
        if config_path:
            path = Path(config_path)
            
            if path.exists():
                try:
                    if path.suffix in ['.yaml', '.yml']:
                        with open(path, 'r', encoding='utf-8') as f:
                            data = yaml.safe_load(f) or {}
                    elif path.suffix == '.json':
                        with open(path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                    else:
                        print(f"⚠ Định dạng file không hỗ trợ: {path.suffix}")
                        return config
                    
                    # Cập nhật cấu hình
                    for key, value in data.items():
                        if hasattr(config, key):
                            setattr(config, key, value)
                    
                    print(f"✓ Đã tải cấu hình từ: {config_path}")
                except Exception as e:
                    print(f"❌ Lỗi tải cấu hình: {e}")
            else:
                print(f"⚠ File cấu hình không tồn tại: {config_path}")
        
        return config
    
    def save(self, config_path: str):
        """
        Lưu cấu hình vào file
        
        Args:
            config_path: Đường dẫn file đích (.yaml hoặc .json)
        """
        path = Path(config_path)
        data = asdict(self)
        
        try:
            if path.suffix in ['.yaml', '.yml']:
                with open(path, 'w', encoding='utf-8') as f:
                    yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
            elif path.suffix == '.json':
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                print(f"❌ Định dạng file không hỗ trợ: {path.suffix}")
                return
            
            print(f"✓ Đã lưu cấu hình vào: {config_path}")
        except Exception as e:
            print(f"❌ Lỗi lưu cấu hình: {e}")
    
    def __str__(self) -> str:
        """In cấu hình"""
        lines = ["Cấu hình hệ thống:", "-" * 40]
        for key, value in asdict(self).items():
            lines.append(f"  {key}: {value}")
        return "\n".join(lines)
