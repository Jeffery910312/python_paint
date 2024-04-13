import tkinter as tk
from tkinter import colorchooser
from tkinter import filedialog
from tkinter import messagebox
import cv2
import os
import numpy as np
import pyautogui

class PaintApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python小畫家")
        
        self.pen_color = "#000000"
        self.pen_size = 2
        self.is_pen = True
        self.is_eraser = False
        self.is_fill_mode = False 
        
        self.undo_stack = []  # 用于保存绘图历史记录
        self.redo_stack = []  # 用于保存撤销的操作，以便撤销撤销（重做）
        self.max_history_length = 10
        
        self.canvas = tk.Canvas(self.root, bg="white", width=1200, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<Button-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.config(cursor="pencil") 

        self.pen_btn = tk.Button(self.root, text="筆", command=self.choose_pen)
        self.pen_btn.pack(side=tk.LEFT)

        self.erase_btn = tk.Button(self.root, text="橡皮擦", command=self.choose_erase)
        self.erase_btn.pack(side=tk.LEFT)

        self.fill_btn = tk.Button(self.root, text="填色", command=self.toggle_fill_mode)
        self.fill_btn.pack(side=tk.LEFT)
        
        self.color_btn = tk.Button(self.root, text="顏色", command=self.choose_color)
        self.color_btn.pack(side=tk.LEFT)

        self.size_slider = tk.Scale(self.root, from_=1, to=10, orient=tk.HORIZONTAL, label="大小", command=self.change_size)
        self.size_slider.pack(side=tk.LEFT)

        self.save_btn = tk.Button(self.root, text="保存", command=self.save_image)
        self.save_btn.pack(side=tk.RIGHT)

        self.load_btn = tk.Button(self.root, text="加載", command=self.load_image)
        self.load_btn.pack(side=tk.RIGHT)

        self.redo_btn = tk.Button(self.root, text="取消復原", command=self.redo)
        self.redo_btn.pack(side=tk.RIGHT)

        self.undo_btn = tk.Button(self.root, text="復原", command=self.undo)
        self.undo_btn.pack(side=tk.RIGHT)
        
        self.clear_btn = tk.Button(self.root, text="清除", command=self.clear_canvas)
        self.clear_btn.pack(side=tk.RIGHT)

        self.gaussian_btn = tk.Button(self.root, text="Gaussian Blur", command=self.apply_gaussian_blur)
        self.gaussian_btn.pack(side=tk.LEFT)

        self.canny_btn = tk.Button(self.root, text="Canny", command=self.apply_canny)
        self.canny_btn.pack(side=tk.LEFT)

        self.Speia_btn = tk.Button(self.root, text="Sepia", command=self.apply_Speia)
        self.Speia_btn.pack(side=tk.LEFT)

        self.Emboss_btn = tk.Button(self.root, text="Emboss", command=self.apply_Emboss)
        self.Emboss_btn.pack(side=tk.LEFT)
        
        
        

    def toggle_fill_mode(self):
        self.is_pen = False
        self.is_eraser = False
        self.is_fill_mode = True
        self.canvas.config(cursor="target")  # 更改鼠标样式
        self.canvas.bind("<Button-1>", self.fill_color_at_click)  # 绑定填充功能

    def fill_color_at_click(self, event):
        if self.is_fill_mode:
            x, y = event.x , event.y
            fill_color = self.pen_color  # 填充颜色为当前画笔颜色
            self.paint_bucket(x, y, fill_color)
            print("Mouse click coordinates (x, y):", x, y)

    def paint_bucket(self, x, y, fill_color):
        # 将画布内容转换为OpenCV格式
        canvas_image = self.get_canvas_image()

        # 创建掩码
        mask = np.zeros((canvas_image.shape[0] + 2, canvas_image.shape[1] + 2), dtype=np.uint8)

        # 将填充颜色转换为OpenCV格式
        new_fill_color = tuple(int(fill_color[i:i+2], 16) for i in (5, 3, 1))  

        seed_point = (x, y)

        lo_diff = up_diff = (0, 0, 0)
        # 执行泛洪填充算法
        _, filled_image, _, _ = cv2.floodFill(canvas_image, mask, seed_point, new_fill_color, lo_diff, up_diff)
        
        # 将当前画布状态保存到撤销栈中
        self.undo_stack.append(self.get_canvas_image().copy())
        
        # 显示填充后的图像
        self.show_image(filled_image)

    def draw(self, event):
        x1, y1 = (event.x - self.pen_size), (event.y - self.pen_size)
        x2, y2 = (event.x + self.pen_size), (event.y + self.pen_size)
        if self.is_pen:
            self.canvas.create_oval(x1, y1, x2, y2, fill=self.pen_color, outline=self.pen_color)
        elif self.is_eraser:
            self.canvas.create_oval(x1, y1, x2, y2, fill="white", outline="white")

    def on_press(self, event):
        # 在鼠标按下前保存一次画布状态
        self.undo_stack.append(self.get_canvas_image().copy())
            

    def choose_pen(self):
        self.canvas.config(cursor="pencil") 
        self.is_pen = True
        self.is_eraser = False
        self.is_fill_mode = False

        
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
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp")])
        if file_path:
            # 处理中文路径
            file_path = os.fsencode(file_path).decode('utf-8')
            image = cv2.imread(file_path)
            if image is not None:
                self.show_image(image)
                self.undo_stack.append(self.get_canvas_image().copy())
            else:
                messagebox.showinfo('警告', '無法開啟檔案')


    def save_image(self):
        file_path = filedialog.asksaveasfilename(filetypes=[('JPG', '*.jpg')],defaultextension=".jpg")

        if file_path:
            file_path = os.fsencode(file_path).decode('utf-8')
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
        
        # 将当前画布状态保存到撤销栈中
        self.undo_stack.append(self.get_canvas_image().copy())

    def change_size(self, val):
        self.pen_size = int(val)
  
    def get_canvas_image(self):
        # 获取画布左上角相对于程序窗口左上角的坐标
        canvas_x0 = 0  # 画布在程序窗口中的左上角 x 坐标
        canvas_y0 = 0  # 画布在程序窗口中的左上角 y 坐标

        # 获取画布的宽度和高度
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # 在截图时使用相对于屏幕左上角的边界框参数
        x0 = self.canvas.winfo_rootx() + canvas_x0
        y0 = self.canvas.winfo_rooty() + canvas_y0

        # 截取画布区域的截图
        screenshot = pyautogui.screenshot(region=(x0, y0, canvas_width, canvas_height))

        # 将截图转换为 numpy 数组，并转换为 RGB 格式
        canvas_image = np.array(screenshot)
        canvas_image_rgb = cv2.cvtColor(canvas_image, cv2.COLOR_BGR2RGB)
        

        return canvas_image_rgb
    
    def apply_gaussian_blur(self, kernel_size=(5, 5)):
        # 获取画布上的内容并转换为图像
        canvas_image = self.get_canvas_image()

        # 对图像应用高斯模糊
        blurred_image = cv2.GaussianBlur(canvas_image, kernel_size, 0)

        resized_blurred_image = cv2.resize(blurred_image, (self.canvas.winfo_width(), self.canvas.winfo_height()))

        # 在画布上显示模糊后的图像
        self.show_image(resized_blurred_image)
        self.undo_stack.append(self.get_canvas_image().copy())

    def apply_canny(self):
        # 获取画布上的内容并转换为图像
        canvas_image = self.get_canvas_image()

        # 将图像从BGR格式转换为灰度图
        gray_image = cv2.cvtColor(canvas_image, cv2.COLOR_BGR2GRAY)

        # 对灰度图应用Canny边缘检测
        edges = cv2.Canny(gray_image, 50, 150)  # 50和150是Canny算法中的低阈值和高阈值

        self.show_image(edges)
        self.undo_stack.append(self.get_canvas_image().copy())
    
    def apply_Speia(self):
        canvas_image = self.get_canvas_image()

        # SEPIA效果
        sepia_matrix = np.array([[0.272, 0.534, 0.131],
                                [ 0.349, 0.686, 0.168],
                                [ 0.393, 0.769, 0.189]])
        
        sepia_image = cv2.transform(canvas_image, sepia_matrix)

        self.show_image(sepia_image)
        self.undo_stack.append(self.get_canvas_image().copy())

    def apply_Emboss(self):
        canvas_image = self.get_canvas_image()

        # 将图像转换为灰度图像
        gray_image = cv2.cvtColor(canvas_image, cv2.COLOR_BGR2GRAY)

        # EMBOSS效果
        emboss_kernel = np.array([[-2., -1., 0.],
                                  [-1., 1., 1. ], 
                                  [ 0., 1., 2. ]])
            
        emboss_image = cv2.filter2D(gray_image, -1, emboss_kernel)


        self.show_image(emboss_image)
        self.undo_stack.append(self.get_canvas_image().copy())

    def add_to_undo_stack(self, item):
        self.undo_stack.append(item)
        # 如果操作历史记录的长度超过限制，则删除最旧的条目
        if len(self.undo_stack) > self.max_history_length:
            self.undo_stack.pop(0)

    def add_to_redo_stack(self, item):
        self.redo_stack.append(item)
        # 如果操作历史记录的长度超过限制，则删除最旧的条目
        if len(self.redo_stack) > self.max_history_length:
            self.redo_stack.pop(0)

    def undo(self):
        if self.undo_stack:
            # 将当前画布状态保存到重做栈中
            self.add_to_redo_stack(self.get_canvas_image().copy())
            # 从撤销栈中弹出上一个画布状态
            prev_canvas_image = self.undo_stack.pop()
            # 在画布上显示上一个画布状态
            self.show_image(prev_canvas_image)
        else:
            messagebox.showinfo('提示', '無法執行撤銷操作，沒有可用的歷史記錄')

    def redo(self):
        if self.redo_stack:
            # 将当前画布状态保存到撤销栈中
            self.add_to_undo_stack(self.get_canvas_image().copy())
            # 从重做栈中弹出上一个画布状态
            prev_canvas_image = self.redo_stack.pop()
            # 在画布上显示上一个画布状态
            self.show_image(prev_canvas_image)
        else:
            messagebox.showinfo('提示', '無法執行撤銷操作，沒有可用的歷史記錄')

if __name__ == "__main__":
    root = tk.Tk()
    paint_app = PaintApp(root)
    root.mainloop()
