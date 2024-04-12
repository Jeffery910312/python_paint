import tkinter as tk
from tkinter import colorchooser
from tkinter import filedialog
from PIL import Image
from collections import deque
import cv2
import numpy as np
import io



class PaintApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python小畫家")
        
        self.pen_color = "#000000"
        self.pen_size = 2
        self.is_pen = True
        self.is_eraser = False
        self.is_fill_mode = False 
        
        
        self.canvas = tk.Canvas(self.root, bg="white", width=600, height=400)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.config(cursor="pencil") 

        self.pen_btn = tk.Button(self.root, text="筆", command=self.choose_pen)
        self.pen_btn.pack(side=tk.LEFT)

        self.erase_btn = tk.Button(self.root, text="橡皮擦", command=self.choose_erase)
        self.erase_btn.pack(side=tk.LEFT)

        self.load_btn = tk.Button(self.root, text="加載", command=self.load_image)
        self.load_btn.pack(side=tk.LEFT)

        self.save_btn = tk.Button(self.root, text="保存", command=self.save_image)
        self.save_btn.pack(side=tk.LEFT)
        
        self.color_btn = tk.Button(self.root, text="填色", command=self.toggle_fill_mode)
        self.color_btn.pack(side=tk.LEFT)
        
        self.color_btn = tk.Button(self.root, text="顏色", command=self.choose_color)
        self.color_btn.pack(side=tk.LEFT)
        
        self.clear_btn = tk.Button(self.root, text="清除", command=self.clear_canvas)
        self.clear_btn.pack(side=tk.LEFT)

        self.clear_btn = tk.Button(self.root, text="Gaussian Blur", command=self.apply_gaussian_blur)
        self.clear_btn.pack(side=tk.LEFT)

        self.clear_btn = tk.Button(self.root, text="Canny", command=self.apply_canny)
        self.clear_btn.pack(side=tk.LEFT)
        
        
        self.size_slider = tk.Scale(self.root, from_=1, to=10, orient=tk.HORIZONTAL, label="大小", command=self.change_size)
        self.size_slider.pack(side=tk.LEFT)
        

    def toggle_fill_mode(self):
        self.is_pen = False
        self.is_eraser = False
        self.is_fill_mode = True
        self.canvas.config(cursor="target")  # 更改鼠标样式
        self.canvas.bind("<Button-1>", self.fill_color_at_click)  # 绑定填充功能

    def fill_color_at_click(self, event):
        if self.is_fill_mode:
            x, y = self.mouse_click_to_canvas_coords(event)
            fill_color = self.pen_color  # 填充颜色为当前画笔颜色
            self.paint_bucket(x, y, fill_color)
            print("Mouse click coordinates (x, y):", x, y)

    def mouse_click_to_canvas_coords(self, event):
        # 获取鼠标点击的坐标
        x_raw, y_raw = event.x, event.y
        # 获取绘图区域的大小
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        # 计算绘图区域中鼠标点击的相对位置
        x_canvas = int(x_raw * (canvas_width / self.canvas.winfo_reqwidth()))
        y_canvas = int(y_raw * (canvas_height / self.canvas.winfo_reqheight()))
        # 返回转换后的坐标
        print(x_raw)
        print(x_canvas)
        return x_canvas, y_canvas



    def paint_bucket(self, x, y, fill_color):
        # 将画布内容转换为OpenCV格式
        canvas_image = self.get_canvas_image()

        # 创建掩码
        mask = np.zeros((canvas_image.shape[0] + 2, canvas_image.shape[1] + 2), dtype=np.uint8)

        # 将填充颜色转换为OpenCV格式
        new_fill_color = tuple(int(fill_color[i:i+2], 16) for i in (1, 3, 5))  # 将十六进制颜色转换为BGR格式

        # 确保种子点在图像范围内
        if 0 <= x < canvas_image.shape[1] and 0 <= y < canvas_image.shape[0]:
            # 如果鼠标点击坐标在图像范围内，直接使用该坐标作为种子点
            seed_point = (x, y)
        else:
            # 如果鼠标点击坐标超出了图像范围，调整种子点的位置
            adjusted_x = max(0, min(x, canvas_image.shape[1] - 1))
            adjusted_y = max(0, min(y, canvas_image.shape[0] - 1))
            seed_point = (adjusted_x, adjusted_y)

        lo_diff = up_diff = (0, 0, 0)
        # 执行泛洪填充算法
        _, filled_image, _, _ = cv2.floodFill(canvas_image, mask, seed_point, new_fill_color, lo_diff, up_diff)
        # 显示填充后的图像
        filled_image = cv2.resize(filled_image, (self.canvas.winfo_width(), self.canvas.winfo_height()))
        self.show_image(filled_image)







    def draw(self, event):
        x1, y1 = (event.x - self.pen_size), (event.y - self.pen_size)
        x2, y2 = (event.x + self.pen_size), (event.y + self.pen_size)
        if not self.is_eraser:
            self.canvas.create_oval(x1, y1, x2, y2, fill=self.pen_color, outline=self.pen_color)
        else:
            self.canvas.create_oval(x1, y1, x2, y2, fill="white", outline="white")

    def choose_pen(self):
        self.canvas.config(cursor="pencil") 
        self.is_pen = True
        self.is_eraser = False
        self.is_fill_mode = False
        self.is_fill_mode
        
    def choose_erase(self):
        self.canvas.config(cursor="dot") 
        self.is_pen = False
        self.is_eraser = True
        self.is_fill_mode = False
        
    def choose_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.pen_color = color

    def load_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            image = cv2.imread(file_path)
            if image is not None:
                self.show_image(image)

    def save_image(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".jpg")
        if file_path:
            canvas_image = self.get_canvas_image()
            cv2.imwrite(file_path, canvas_image)

    def show_image(self, image):
        # 清除 Canvas 上的內容
        self.canvas.delete("all")

        # 将 OpenCV 格式的图像转换为 PhotoImage
        image_bytes = cv2.imencode('.png', image)[1].tobytes()
        self.image_tk = tk.PhotoImage(data=image_bytes)

        # 在 Canvas 上显示图像
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image_tk)

        

            
    def clear_canvas(self):
        self.canvas.delete("all")
        
    def change_size(self, val):
        self.pen_size = int(val)

    def get_canvas_image(self):
        # 获取画布上的内容并转换为图像
        canvas_image = self.canvas.postscript(colormode="color")
        image = Image.open(io.BytesIO(canvas_image.encode("utf-8")))
        image = np.array(image)

        # 将图像从BGR格式转换为RGB格式
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        return image_rgb
    
    def apply_gaussian_blur(self, kernel_size=(5, 5)):
        # 获取画布上的内容并转换为图像
        canvas_image = self.get_canvas_image()

        # 对图像应用高斯模糊
        blurred_image = cv2.GaussianBlur(canvas_image, kernel_size, 0)

        resized_blurred_image = cv2.resize(blurred_image, (self.canvas.winfo_width(), self.canvas.winfo_height()))

        # 在画布上显示模糊后的图像
        self.show_image(resized_blurred_image)

    def apply_canny(self):
        # 获取画布上的内容并转换为图像
        canvas_image = self.get_canvas_image()

        # 将图像从BGR格式转换为灰度图
        gray_image = cv2.cvtColor(canvas_image, cv2.COLOR_BGR2GRAY)

        # 对灰度图应用Canny边缘检测
        edges = cv2.Canny(gray_image, 50, 150)  # 50和150是Canny算法中的低阈值和高阈值

        resized_edges = cv2.resize(edges, (self.canvas.winfo_width(), self.canvas.winfo_height()))


        self.show_image(resized_edges)




if __name__ == "__main__":
    root = tk.Tk()
    paint_app = PaintApp(root)
    root.mainloop()
