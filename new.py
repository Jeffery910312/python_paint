import tkinter as tk
from tkinter import colorchooser
from tkinter import filedialog
import cv2
import numpy as np

class PaintApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python小畫家")
        
        self.pen_color = "black"
        self.pen_size = 2
        self.is_eraser = False
        
        self.canvas = tk.Canvas(self.root, bg="white", width=600, height=400)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.canvas.bind("<B1-Motion>", self.draw)

        self.pen_btn = tk.Button(self.root, text="筆", command=self.choose_pen)
        self.pen_btn.pack(side=tk.LEFT)

        self.erase_btn = tk.Button(self.root, text="橡皮擦", command=self.choose_erase)
        self.erase_btn.pack(side=tk.LEFT)

        self.load_btn = tk.Button(self.root, text="加載", command=self.load_image)
        self.load_btn.pack(side=tk.LEFT)

        self.save_btn = tk.Button(self.root, text="保存", command=self.save_image)
        self.save_btn.pack(side=tk.LEFT)
        
        self.color_btn = tk.Button(self.root, text="填色", command=self.fill)
        self.color_btn.pack(side=tk.LEFT)
        
        self.color_btn = tk.Button(self.root, text="顏色", command=self.choose_color)
        self.color_btn.pack(side=tk.LEFT)
        
        self.clear_btn = tk.Button(self.root, text="清除", command=self.clear_canvas)
        self.clear_btn.pack(side=tk.LEFT)
        
        self.size_slider = tk.Scale(self.root, from_=1, to=10, orient=tk.HORIZONTAL, label="大小", command=self.change_size)
        self.size_slider.pack(side=tk.LEFT)
        
    def draw(self, event):
        x1, y1 = (event.x - self.pen_size), (event.y - self.pen_size)
        x2, y2 = (event.x + self.pen_size), (event.y + self.pen_size)
        if not self.is_eraser:
            self.canvas.create_oval(x1, y1, x2, y2, fill=self.pen_color, outline=self.pen_color)
        else:
            self.canvas.create_oval(x1, y1, x2, y2, fill="white", outline="white")

    def choose_pen(self):
        self.is_eraser = False
        
    def choose_erase(self):
        self.is_eraser = True
        
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

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        height, width, _ = image_rgb.shape
        image_bytes = cv2.imencode('.png', image_rgb)[1].tobytes()
        self.image_tk = tk.PhotoImage(data=image_bytes)

        # 將 Canvas 設置為與圖片大小相符
        self.canvas.config(width=width, height=height)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image_tk)

        
    def fill(self):
        self.canvas.create_rectangle(0, 0, self.canvas.winfo_width(), self.canvas.winfo_height(), fill=self.pen_color)
            
    def clear_canvas(self):
        self.canvas.delete("all")
        
    def change_size(self, val):
        self.pen_size = int(val)

    def get_canvas_image(self):
        x0 = self.canvas.winfo_rootx() + self.canvas.winfo_x()
        y0 = self.canvas.winfo_rooty() + self.canvas.winfo_y()
        x1 = x0 + self.canvas.winfo_width()
        y1 = y0 + self.canvas.winfo_height()
        canvas_color = self.canvas.winfo_rgb(self.canvas.cget('bg'))
        screenshot = np.array(canvas_color, dtype=np.uint8).reshape((1, 1, 3))
        screenshot = np.repeat(screenshot, (y1 - y0) * (x1 - x0), axis=0).reshape((y1 - y0, x1 - x0, 3))
        return screenshot


if __name__ == "__main__":
    root = tk.Tk()
    paint_app = PaintApp(root)
    root.mainloop()
