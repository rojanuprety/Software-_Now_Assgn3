import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2

class ImageEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Crop & Resize App")

        self.image = None 
        self.cropped = None  

        self.canvas = tk.Canvas(root, cursor="cross")
        self.canvas.grid(row=0, column=0, columnspan=2)

        self.start_x = self.start_y = self.rect = None

        # Buttons
        tk.Button(root, text="Load Image", command=self.load_image).grid(row=1, column=0, sticky="ew")
        tk.Button(root, text="Save Image", command=self.save_image).grid(row=1, column=1, sticky="ew")

        # Resize slider
        self.scale = tk.Scale(root, from_=10, to=200, orient='horizontal', label="Resize %", command=self.resize_image)
        self.scale.set(100)
        self.scale.grid(row=2, column=0, columnspan=2, sticky="ew")

        # Event bindings
        self.canvas.bind("<Button-1>", self.start_crop)
        self.canvas.bind("<B1-Motion>", self.draw_crop)
        self.canvas.bind("<ButtonRelease-1>", self.finish_crop)

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.jpeg *.bmp")])
        if file_path:
            self.image = cv2.cvtColor(cv2.imread(file_path), cv2.COLOR_BGR2RGB)
            self.display_image(self.image)

    def display_image(self, img):
        self.tk_image = ImageTk.PhotoImage(Image.fromarray(img))
        self.canvas.config(width=self.tk_image.width(), height=self.tk_image.height())
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)

    def start_crop(self, event):
        if self.image is None:
            return
        self.start_x, self.start_y = event.x, event.y
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red")

    def draw_crop(self, event):
        if self.rect:
            self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def finish_crop(self, event):
        if self.image is None:
            return
        x1, y1 = self.start_x, self.start_y
        x2, y2 = event.x, event.y
        x1, x2 = sorted([x1, x2])
        y1, y2 = sorted([y1, y2])
        self.cropped = self.image[y1:y2, x1:x2]
        if self.cropped.size == 0:
            messagebox.showerror("Error", "Invalid crop area.")
            return
        self.display_image(self.cropped)

    def resize_image(self, value):
        if self.cropped is None:
            return
        scale = int(value) / 100
        new_size = (int(self.cropped.shape[1] * scale), int(self.cropped.shape[0] * scale))
        resized = cv2.resize(self.cropped, new_size)
        self.display_image(resized)

    def save_image(self):
        if self.cropped is None:
            messagebox.showwarning("Warning", "No image to save.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if file_path:
            scale = self.scale.get() / 100
            resized = cv2.resize(self.cropped, (int(self.cropped.shape[1] * scale), int(self.cropped.shape[0] * scale)))
            cv2.imwrite(file_path, cv2.cvtColor(resized, cv2.COLOR_RGB2BGR))
            messagebox.showinfo("Saved", "Image saved successfully.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditorApp(root)
    root.mainloop()
