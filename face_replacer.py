import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageTk
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import sys
import ctypes
import base64
import io

try:
    if sys.platform == 'win32':
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass


class ElementInfo:
    def __init__(self, name, x, y, width, height, color):
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.source_img = None
        self.original_source = None


class FaceReplacer:
    def __init__(self):
        self.image = None
        self.image_copy = None
        self.mouse_pos = None
        self.result_image = None
        
        self.elements = {}
        self.selected_element = None
        self.dragging = False
        self.drag_start = None
        self.resize_handle = None
        
        self.preset_eye_left = None
        self.preset_eye_right = None
        self.preset_mouth = None
        
        self.load_embedded_presets()
        
    def load_embedded_presets(self):
        self.preset_eye_left = self.load_preset_image("preset_eye_left.png")
        self.preset_eye_right = self.load_preset_image("preset_eye_right.png")
        self.preset_mouth = self.load_preset_image("preset_mouth.png")
        
    def load_preset_image(self, filename):
        if not os.path.exists(filename):
            raise FileNotFoundError(f"找不到预设图片: {filename}")
        
        try:
            pil_img = Image.open(filename)
            if pil_img.mode != 'RGBA':
                pil_img = pil_img.convert('RGBA')
            return self.pil_to_cv2(pil_img)
        except Exception as e:
            raise RuntimeError(f"加载预设图片失败 {filename}: {e}")
        
    def pil_to_cv2(self, pil_img):
        pil_img = pil_img.convert('RGBA')
        cv2_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGBA2BGRA)
        return cv2_img
        
    def load_image(self, image_path):
        self.image = cv2.imread(image_path)
        if self.image is None:
            raise ValueError(f"无法加载图片: {image_path}")
        self.image_copy = self.image.copy()
        self.reset_elements()
        
    def reset_elements(self):
        img_height, img_width = self.image.shape[:2]
        
        self.elements = {
            "eye_left": ElementInfo("eye_left", img_width // 4, img_height // 3, 100, 60, (255, 0, 0)),
            "eye_right": ElementInfo("eye_right", img_width * 3 // 4, img_height // 3, 100, 60, (0, 255, 0)),
            "mouth": ElementInfo("mouth", img_width // 2, img_height * 2 // 3, 120, 40, (0, 0, 255))
        }
        
        self.selected_element = None
        self.dragging = False
        self.drag_start = None
        self.resize_handle = None
        
    def mouse_callback(self, event, x, y, flags, param):
        self.mouse_pos = (x, y)
        
        if event == cv2.EVENT_LBUTTONDOWN:
            self.handle_click(x, y)
        elif event == cv2.EVENT_LBUTTONUP:
            self.dragging = False
            self.resize_handle = None
        elif event == cv2.EVENT_MOUSEMOVE and (self.dragging or self.resize_handle):
            self.handle_drag(x, y)
            
    def handle_click(self, x, y):
        handle_size = 8
        
        for name, elem in self.elements.items():
            handles = self.get_resize_handles(elem)
            
            for handle_name, (hx, hy) in handles.items():
                if abs(x - hx) < handle_size and abs(y - hy) < handle_size:
                    self.resize_handle = (name, handle_name)
                    self.drag_start = (x, y)
                    return
                    
            if x >= elem.x and x <= elem.x + elem.width and y >= elem.y and y <= elem.y + elem.height:
                self.selected_element = name
                self.dragging = True
                self.drag_start = (x, y)
                return
                
    def handle_drag(self, x, y):
        if self.resize_handle:
            name, handle_name = self.resize_handle
            elem = self.elements[name]
            dx = x - self.drag_start[0]
            dy = y - self.drag_start[1]
            
            if handle_name == "top_left":
                elem.x += dx
                elem.y += dy
                elem.width -= dx
                elem.height -= dy
            elif handle_name == "top_right":
                elem.y += dy
                elem.width += dx
                elem.height -= dy
            elif handle_name == "bottom_left":
                elem.x += dx
                elem.width -= dx
                elem.height += dy
            elif handle_name == "bottom_right":
                elem.width += dx
                elem.height += dy
            elif handle_name == "top":
                elem.y += dy
                elem.height -= dy
            elif handle_name == "bottom":
                elem.height += dy
            elif handle_name == "left":
                elem.x += dx
                elem.width -= dx
            elif handle_name == "right":
                elem.width += dx
                
            elem.width = max(10, elem.width)
            elem.height = max(10, elem.height)
            self.drag_start = (x, y)
            
        elif self.dragging and self.selected_element:
            elem = self.elements[self.selected_element]
            dx = x - self.drag_start[0]
            dy = y - self.drag_start[1]
            elem.x += dx
            elem.y += dy
            self.drag_start = (x, y)
            
    def get_resize_handles(self, elem):
        handles = {
            "top_left": (elem.x, elem.y),
            "top_right": (elem.x + elem.width, elem.y),
            "bottom_left": (elem.x, elem.y + elem.height),
            "bottom_right": (elem.x + elem.width, elem.y + elem.height),
            "top": (elem.x + elem.width // 2, elem.y),
            "bottom": (elem.x + elem.width // 2, elem.y + elem.height),
            "left": (elem.x, elem.y + elem.height // 2),
            "right": (elem.x + elem.width, elem.y + elem.height // 2)
        }
        return handles
        
    def draw_elements(self):
        display = self.image_copy.copy()
        
        for name, elem in self.elements.items():
            if name == self.selected_element:
                cv2.rectangle(display, (elem.x, elem.y), 
                            (elem.x + elem.width, elem.y + elem.height), 
                            elem.color, 2)
                
                handles = self.get_resize_handles(elem)
                for handle_name, (hx, hy) in handles.items():
                    cv2.circle(display, (hx, hy), 5, (255, 255, 0), -1)
                    cv2.circle(display, (hx, hy), 5, (0, 0, 0), 1)
            else:
                cv2.rectangle(display, (elem.x, elem.y), 
                            (elem.x + elem.width, elem.y + elem.height), 
                            elem.color, 1)
                            
            cv2.putText(display, elem.name, (elem.x, elem.y - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, elem.color, 1)
                       
        return display
        
    def draw_text_with_pil(self, cv_img, text, position, font_size=20, color=(255,255,255)):
        pil_img = Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_img)
        
        try:
            font = ImageFont.truetype("msyh.ttc", font_size)
        except:
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
                
        draw.text(position, text, font=font, fill=color)
        
        return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        
    def get_instruction_text(self):
        return "拖动元素调整位置，拖动控制点调整大小，按S保存结果，按ESC退出"
        
    def run(self, image_path):
        self.load_image(image_path)
        
        cv2.namedWindow("Face Replacer")
        cv2.setMouseCallback("Face Replacer", self.mouse_callback)
        
        while True:
            display = self.draw_elements()
            instruction = self.get_instruction_text()
            
            display = self.draw_text_with_pil(display, instruction, (10, 10), 20, (255, 255, 255))
            display = self.draw_text_with_pil(display, instruction, (12, 12), 20, (0, 0, 0))
            
            cv2.imshow("Face Replacer", display)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == 27:
                break
            elif key == ord('s') or key == ord('S'):
                self.replace_features()
                cv2.imwrite("output.png", self.image)
                self.result_image = self.image.copy()
                print("结果已保存为 output.png")
                break
                    
        cv2.destroyAllWindows()
        
    def replace_features(self):
        for name, elem in self.elements.items():
            if name == "eye_left" and self.preset_eye_left is not None:
                self.replace_region(elem, self.preset_eye_left)
            elif name == "eye_right" and self.preset_eye_right is not None:
                self.replace_region(elem, self.preset_eye_right)
            elif name == "mouth" and self.preset_mouth is not None:
                self.replace_region(elem, self.preset_mouth)
                    
    def replace_region(self, elem, source_img):
        x, y, w, h = elem.x, elem.y, elem.width, elem.height
        
        if w < 1 or h < 1:
            return
            
        resized_source = cv2.resize(source_img, (w, h), interpolation=cv2.INTER_LINEAR)
        
        if resized_source.shape[2] == 4:
            alpha = resized_source[:, :, 3] /255.0
            alpha = alpha[:, :, np.newaxis]
            
            for c in range(3):
                self.image[y:y+h, x:x+w, c] = (
                    alpha[:, :, 0] * resized_source[:, :, c] + 
                    (1 - alpha[:, :, 0]) * self.image[y:y+h, x:x+w, c]
                )
        else:
            self.image[y:y+h, x:x+w] = resized_source


class FaceReplacerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Replacer - 947")
        self.root.geometry("1000x1200")
        
        self.replacer = FaceReplacer()
        self.image_path = None
        
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        ttk.Label(main_frame, text="Face Replacer - 947", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        ttk.Button(main_frame, text="选择图片", command=self.select_image).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.path_label = ttk.Label(main_frame, text="未选择图片", foreground="gray")
        self.path_label.grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)
        
        ttk.Button(main_frame, text="开始处理", command=self.start_processing).grid(row=2, column=0, sticky=tk.W, pady=5)
        
        preview_frame = ttk.LabelFrame(main_frame, text="预览", padding="5")
        preview_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        
        self.preview_label = ttk.Label(preview_frame, text="处理完成后在此预览结果", anchor="center")
        self.preview_label.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Button(main_frame, text="保存结果", command=self.save_result).grid(row=4, column=0, sticky=tk.W, pady=5)
        
        info_frame = ttk.LabelFrame(main_frame, text="使用说明", padding="5")
        info_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        info_text = """1. 点击"选择图片"选择图片
2. 点击"开始处理"打开编辑窗口
3. 拖动调整图片上左眼、右眼和嘴巴的位置
4. 拖动控制点调整大小（8个控制点）
5. 按 'S' 保存结果
6. 按 'ESC' 退出程序"""
        
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).grid(row=0, column=0, sticky=tk.W)
        
    def select_image(self):
        file_path = filedialog.askopenfilename(
            title="选择图片",
            filetypes=[("图片文件", "*.png *.jpg *.jpeg *.bmp *.gif"), ("所有文件", "*.*")]
        )
        
        if file_path:
            self.image_path = file_path
            self.path_label.config(text=os.path.basename(file_path))
            
    def start_processing(self):
        if not self.image_path:
            messagebox.showwarning("警告", "请先选择一张图片")
            return
            
        try:
            self.replacer.run(self.image_path)
            
            if self.replacer.result_image is not None:
                self.show_preview()
                messagebox.showinfo("完成", "处理完成！结果已保存为 output.png")
        except Exception as e:
            messagebox.showerror("错误", f"处理失败: {str(e)}")
            
    def show_preview(self):
        if self.replacer.result_image is None:
            return
            
        result_rgb = cv2.cvtColor(self.replacer.result_image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(result_rgb)
        
        max_size = 400
        img_width, img_height = pil_image.size
        
        if img_width > max_size or img_height > max_size:
            ratio = min(max_size / img_width, max_size / img_height)
            new_width = int(img_width * ratio)
            new_height = int(img_height * ratio)
            pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        photo = ImageTk.PhotoImage(pil_image)
        self.preview_label.config(image=photo, text="")
        self.preview_label.image = photo
        self.preview_label.photo = photo
        
    def save_result(self):
        if self.replacer.result_image is None:
            messagebox.showwarning("警告", "没有可保存的结果")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="保存结果",
            defaultextension=".png",
            filetypes=[("PNG图片", "*.png"), ("JPEG图片", "*.jpg"), ("所有文件", "*.*")]
        )
        
        if file_path:
            cv2.imwrite(file_path, self.replacer.result_image)
            messagebox.showinfo("成功", f"结果已保存到: {file_path}")


if __name__ == "__main__":
    root = tk.Tk()
    app = FaceReplacerGUI(root)
    root.mainloop()
