import cv2
import moviepy.editor as mp
import numpy as np
from PIL import Image, ImageDraw, ImageFont

class VideoEditor:
    def __init__(self, video_path, item_image_path, prices, icon_paths, output_path):
        # Cài đặt đường dẫn và tham số
        self.video_path = video_path
        self.item_image_path = item_image_path
        self.output_path = output_path
        self.prices = prices
        self.icon_paths = icon_paths
        self.mobile_width, self.mobile_height = 1080, 1920

        # Tải video nền và làm tối nền
        self.background_video = mp.VideoFileClip(self.video_path).resize((self.mobile_width, self.mobile_height)).without_audio()
        self.background_video = self.background_video.fl_image(lambda frame: (frame * 0.6).astype(np.uint8))

        # Tải ảnh sản phẩm và các biểu tượng, thay đổi kích thước
        self.item_image = Image.open(self.item_image_path).convert("RGBA").resize((300, 300))
        self.icons = [Image.open(icon_path).resize((300, 300)).convert("RGBA") for icon_path in self.icon_paths]

        # Tạo danh sách nền giá
        self.price_tags = [self.create_price_tag(price) for price in self.prices]

        # Vị trí của các hàng (sản phẩm, biểu tượng, giá) trên video
        self.item_positions = [
            (50, 200),       # Hàng trên cùng
            (50, 700),       # Hàng giữa
            (50, 1200)       # Hàng dưới cùng
        ]
    
    def create_price_tag(self, price_text):
        # Tạo nền trắng cho giá với kích thước 300x300 và chèn giá lên đó
        price_tag = Image.new("RGBA", (300, 300), "white")
        draw = ImageDraw.Draw(price_tag)
        
        # Thêm giá vào giữa nền trắng với chữ màu đen
        font = ImageFont.truetype("arial.ttf", 40)
        text_bbox = draw.textbbox((0, 0), price_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # Tính toán vị trí trung tâm
        text_position = ((300 - text_width) // 2, (300 - text_height) // 2)
        draw.text(text_position, price_text, font=font, fill="black")
        
        return price_tag

    def add_items_icons_and_prices(self, frame, t):
        # Chuyển khung hình từ OpenCV thành PIL Image
        pil_frame = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        
        # Đặt alpha dựa trên thời gian: từ giây thứ 1 đến giây thứ 2 (xuất hiện dần trong 1 giây sau giây thứ 1)
        if t < 1:
            alpha = 0  # Ẩn trong 1 giây đầu tiên
        else:
            alpha = int(min(255, 255 * (t - 1) / 3))  # Xuất hiện dần từ giây thứ 1 đến giây thứ 2

        # Dán từng hình sản phẩm, biểu tượng và giá theo hàng
        for i in range(3):
            # Vị trí của các thành phần trong hàng
            product_pos = self.item_positions[i]
            icon_pos = (product_pos[0] + 350, product_pos[1])  # Biểu tượng ở giữa, cách hình sản phẩm
            price_pos = (product_pos[0] + 700, product_pos[1])  # Giá bên phải biểu tượng, cách biểu tượng
            
            # Tạo các lớp alpha cho từng hình
            item_with_alpha = self.item_image.copy()
            item_with_alpha.putalpha(alpha)
            icon_with_alpha = self.icons[i].copy()
            icon_with_alpha.putalpha(alpha)
            price_with_alpha = self.price_tags[i].copy()
            price_with_alpha.putalpha(alpha)
            
            # Dán hình sản phẩm, biểu tượng, và giá theo thứ tự từ trái sang phải với alpha
            pil_frame.paste(item_with_alpha, product_pos, item_with_alpha)
            pil_frame.paste(icon_with_alpha, icon_pos, icon_with_alpha)
            pil_frame.paste(price_with_alpha, price_pos, price_with_alpha)
        
        # Chuyển lại thành OpenCV frame
        return cv2.cvtColor(np.array(pil_frame), cv2.COLOR_RGB2BGR)
    
    def generate_video(self):
        # Áp dụng chức năng thêm item, biểu tượng và giá cho từng khung hình, với hiệu ứng xuất hiện dần dần sau 1 giây
        output_video = self.background_video.fl(lambda gf, t: self.add_items_icons_and_prices(gf(t), t))

        # Xuất video không có âm thanh
        output_video.write_videofile(self.output_path, codec='libx264', fps=24)


# Khởi tạo và chạy VideoEditor
prices = ["199,000 VND", "99,500 VND", "5,000 VND"]
video_path = 'background.mp4'
item_image_path = 'item.png'
icon_paths = ["ga.png", "vit.png", "ngong.png"]
output_path = 'output_video_mobile.mp4'

editor = VideoEditor(video_path, item_image_path, prices, icon_paths, output_path)
editor.generate_video()
