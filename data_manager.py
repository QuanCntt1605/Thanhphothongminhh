"""
Module quản lý dữ liệu nội dung
Tải và lưu trang nội dung từ file
"""

import json
import os
from pathlib import Path
from typing import List
from gui import Page


class DataManager:
    """Quản lý dữ liệu nội dung"""
    
    def __init__(self, data_dir: str = "data"):
        """
        Khởi tạo DataManager
        
        Args:
            data_dir: Thư mục chứa dữ liệu
        """
        self.data_dir = Path(data_dir)
        self.pages_file = self.data_dir / "pages.json"
        
        # Tạo thư mục nếu chưa tồn tại
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def load_pages(self) -> List[Page]:
        """
        Tải danh sách trang từ file
        
        Returns:
            Danh sách các Page objects
        """
        pages = []
        
        # Thử tải từ file JSON
        if self.pages_file.exists():
            try:
                with open(self.pages_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for item in data:
                    page = Page(
                        title=item.get('title', 'Untitled'),
                        content=item.get('content', ''),
                        images=item.get('images', None)
                    )
                    pages.append(page)
                
                print(f"✓ Đã tải {len(pages)} trang từ {self.pages_file}")
                return pages
            except Exception as e:
                print(f"⚠ Lỗi tải từ {self.pages_file}: {e}")
        
        return pages
    
    def save_pages(self, pages: List[Page]):
        """
        Lưu danh sách trang vào file
        
        Args:
            pages: Danh sách các Page objects
        """
        try:
            data = []
            for page in pages:
                data.append({
                    'title': page.title,
                    'content': page.content,
                    'images': page.images
                })
            
            with open(self.pages_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Đã lưu {len(pages)} trang vào {self.pages_file}")
        except Exception as e:
            print(f"❌ Lỗi lưu file: {e}")
    
    def add_page(self, page: Page):
        """
        Thêm một trang mới
        
        Args:
            page: Page object
        """
        pages = self.load_pages()
        pages.append(page)
        self.save_pages(pages)
    
    def get_sample_pages(self) -> List[Page]:
        """
        Tạo các trang mẫu
        
        Returns:
            Danh sách các trang mẫu
        """
        pages = [
            Page(
                title="Thông tin sân bay",
                content="""HÃY CHÀO MỪNG ĐẾN SÂN BAY QUỐC TẾ
                
HƯỚNG DẪN:
• Phòng chờ: Tầng 1
• Nhà vệ sinh: Kế bên quầy check-in
• Cửa hàng miễn thuế: Tầng 2
• Quán ăn: Tầng 2, khu vực C
• Trạm cấp cứu: Bên cạnh sảnh chính

LỊCH BAY HÔMNAY:
→ VN101 Hà Nội 08:45 (Gate 5)
→ VN202 TP.HCM 10:30 (Gate 7)
→ VN303 Đà Nẵng 12:15 (Gate 3)"""
            ),
            Page(
                title="Bản đồ trung tâm thương mại",
                content="""BẢNG DANH SÁCH SHOP
                
TẦNG 1 - THỰC PHẨM & QUẦN ÁO:
✓ Big C - Siêu thị (Khu A)
✓ Zara - Thời trang (Khu B)
✓ H&M - Quần áo (Khu B)
✓ Starbucks - Cà phê (Khu C)

TẦNG 2 - ĐIỆN TỬ & GIẢI TRÍ:
✓ FPT Shop - Điện tử
✓ Apple Store - Quả táo
✓ CGV Cinemas - Rạp chiếu phim
✓ Game Zone - Giải trí

TẦNG 3 - NHƯNG HỌC & SPA:
✓ Thư viện - Đọc sách
✓ Yoga Studio - Tập yoga
✓ Thai Massage - Massage Thái"""
            ),
            Page(
                title="Thông tin bệnh viện",
                content="""BỆNH VIỆN QUỐC TẾ
                
PHÒNG KHÁM:
🏥 Khoa ngoài: Tầng 2, phòng 201-210
🏥 Khoa trong: Tầng 2, phòng 211-220
🏥 Nhi khoa: Tầng 3, phòng 301-310
🏥 Sản phụ khoa: Tầng 3, phòng 311-320
🏥 Phòng mổ: Tầng 4 (Chỉ nhân viên)

GIỜ LÀM VIỆC:
📞 Thứ 2 - Thứ 6: 7:00 - 18:00
📞 Thứ 7: 7:00 - 12:00
📞 Chủ nhật: NGHỈ

LIÊN HỆ:
Đường dây nóng: 1900-1234"""
            ),
            Page(
                title="Thời khoá biểu trường học",
                content="""TRƯỜNG ĐẠI HỌC CÔNG NGHỆ
                
LỚP HỌC THỨ HAI:
🕐 07:00 - 08:30: Nhập môn CNPM
🕐 08:45 - 10:15: Lập trình Java
🕐 10:30 - 12:00: Cơ sở dữ liệu

LỚP HỌC THỨ BA:
🕐 07:00 - 08:30: Web Development
🕐 08:45 - 10:15: Thiết kế giao diện
🕐 10:30 - 12:00: Quản lý dự án

LỚP HỌC THỨ TƯ:
🕐 07:00 - 08:30: Machine Learning
🕐 08:45 - 10:15: Bảo mật mạng
🕐 10:30 - 12:00: Kiểm thử phần mềm

SINH VIÊN ĐƯỢC ỐN TRONG THỜI GIAN HỌC"""
            ),
            Page(
                title="Giá vé xe buýt",
                content="""HỌC GIÁ VÉ XE BUÝT CÔNG CỘNG
                
LOẠI VÉ HÀNG NGÀY:
🚌 Vé lẻ: 5,000 VNĐ / chuyến
🚌 Vé tháng: 300,000 VNĐ / người
🚌 Vé học sinh: 150,000 VNĐ / tháng
🚌 Vé người cao tuổi: Miễn phí

TUYẾN CHÍNH:
#1: Trung tâm → Sân bay (50 phút)
#2: Trung tâm → Bến xe (45 phút)
#3: Trung tâm → Đại học (30 phút)
#4: Trung tâm → Bệnh viện (25 phút)

GIỜ HOẠT ĐỘNG:
Từ 05:00 - 22:00 hàng ngày
Mỗi tuyến cứ 10-15 phút một chuyến"""
            )
        ]
        
        return pages
    
    def create_sample_data(self):
        """Tạo dữ liệu mẫu"""
        pages = self.get_sample_pages()
        self.save_pages(pages)
        print(f"✓ Đã tạo {len(pages)} trang mẫu")
