import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk
import os

class ImageEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Editor")
        self.root.geometry("1200x800")
        
        # Image data below
        self.original_image = None
        self.display_image = None
        self.cropped_image = None
        self.history = []  # For undo/redo
        self.history_index = -1
        
        # Crop variables below
        self.cropping = False
        self.start_x = None
        self.start_y = None
        self.rect = None
        
        # Setup GUI
        self.setup_gui()
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-o>', lambda event: self.load_image())
        self.root.bind('<Control-s>', lambda event: self.save_image())
        self.root.bind('<Control-z>', lambda event: self.undo())
        self.root.bind('<Control-y>', lambda event: self.redo())

    def setup_gui(self):
        # Frames
        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        self.image_frame = tk.Frame(self.root)
        self.image_frame.pack(expand=True, fill=tk.BOTH)
        
        # Buttons
        tk.Button(self.control_frame, text="Load Image (Ctrl+O)", command=self.load_image).pack(side=tk.LEFT, padx=5)
        tk.Button(self.control_frame, text="Save Image (Ctrl+S)", command=self.save_image).pack(side=tk.LEFT, padx=5)
        tk.Button(self.control_frame, text="Undo (Ctrl+Z)", command=self.undo).pack(side=tk.LEFT, padx=5)
        tk.Button(self.control_frame, text="Redo (Ctrl+Y)", command=self.redo).pack(side=tk.LEFT, padx=5)
        
        # Additional processing buttons
        tk.Button(self.control_frame, text="Grayscale", command=self.apply_grayscale).pack(side=tk.LEFT, padx=5)
        tk.Button(self.control_frame, text="Blur", command=self.apply_blur).pack(side=tk.LEFT, padx=5)
        
        # Resize slider
        self.scale_label = tk.Label(self.control_frame, text="Resize Scale: 100%")
        self.scale_label.pack(side=tk.LEFT, padx=5)
        self.scale_slider = tk.Scale(self.control_frame, from_=10, to=200, orient=tk.HORIZONTAL, 
                                   command=self.resize_image, length=200)
        self.scale_slider.set(100)
        self.scale_slider.pack(side=tk.LEFT, padx=5)
        
        # Canvas for original image with scrollbars
        self.canvas_original_frame = tk.Frame(self.image_frame)
        self.canvas_original_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.canvas_original = tk.Canvas(self.canvas_original_frame, bg="gray")
        hbar = tk.Scrollbar(self.canvas_original_frame, orient=tk.HORIZONTAL)
        hbar.pack(side=tk.BOTTOM, fill=tk.X)
        hbar.config(command=self.canvas_original.xview)
        vbar = tk.Scrollbar(self.canvas_original_frame, orient=tk.VERTICAL)
        vbar.pack(side=tk.RIGHT, fill=tk.Y)
        vbar.config(command=self.canvas_original.yview)
        self.canvas_original.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        self.canvas_original.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        
        # Canvas for cropped/processed image with scrollbars
        self.canvas_cropped_frame = tk.Frame(self.image_frame)
        self.canvas_cropped_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
        self.canvas_cropped = tk.Canvas(self.canvas_cropped_frame, bg="gray")
        hbar_c = tk.Scrollbar(self.canvas_cropped_frame, orient=tk.HORIZONTAL)
        hbar_c.pack(side=tk.BOTTOM, fill=tk.X)
        hbar_c.config(command=self.canvas_cropped.xview)
        vbar_c = tk.Scrollbar(self.canvas_cropped_frame, orient=tk.VERTICAL)
        vbar_c.pack(side=tk.RIGHT, fill=tk.Y)
        vbar_c.config(command=self.canvas_cropped.yview)
        self.canvas_cropped.config(xscrollcommand=hbar_c.set, yscrollcommand=vbar_c.set)
        self.canvas_cropped.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        
        # Bind mouse events for cropping
        self.canvas_original.bind("<ButtonPress-1>", self.start_crop)
        self.canvas_original.bind("<B1-Motion>", self.draw_crop)
        self.canvas_original.bind("<ButtonRelease-1>", self.end_crop)

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")])
        if file_path:
            try:
                self.original_image = cv2.imread(file_path)
                if self.original_image is None:
                    raise ValueError("Failed to load image")
                self.display_image = self.original_image.copy()
                self.cropped_image = None  # Reset cropped image
                self.history = []  # Reset history
                self.history_index = -1
                self.add_to_history(self.display_image)
                self.update_display()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {str(e)}")

    def update_display(self):
        if self.display_image is None:
            return
        
        # Resize for display
        max_size = 500
        h, w = self.display_image.shape[:2]
        scale = min(max_size / w, max_size / h)
        display_size = (int(w * scale), int(h * scale))
        display_img = cv2.resize(self.original_image, display_size, interpolation=cv2.INTER_AREA)
        
        # Convert to PhotoImage for original image
        display_img = cv2.cvtColor(display_img, cv2.COLOR_BGR2RGB)
        self.photo = ImageTk.PhotoImage(image=Image.fromarray(display_img))
        self.canvas_original.delete("all")
        self.canvas_original.create_image(0, 0, image=self.photo, anchor=tk.NW)
        self.canvas_original.config(scrollregion=(0, 0, display_size[0], display_size[1]))
        
        # Update cropped image if exists
        if self.cropped_image is not None:
            cropped_display = cv2.resize(self.cropped_image, display_size, interpolation=cv2.INTER_AREA)
            cropped_display = cv2.cvtColor(cropped_display, cv2.COLOR_BGR2RGB)
            self.cropped_photo = ImageTk.PhotoImage(image=Image.fromarray(cropped_display))
            self.canvas_cropped.delete("all")
            self.canvas_cropped.create_image(0, 0, image=self.cropped_photo, anchor=tk.NW)
            self.canvas_cropped.config(scrollregion=(0, 0, display_size[0], display_size[1]))

    def start_crop(self, event):
        if self.display_image is None:
            return
        self.cropping = True
        self.start_x = self.canvas_original.canvasx(event.x)
        self.start_y = self.canvas_original.canvasy(event.y)
        if self.rect:
            self.canvas_original.delete(self.rect)
        self.rect = self.canvas_original.create_rectangle(self.start_x, self.start_y, 
                                                       self.start_x, self.start_y, outline="red", dash=(4, 4))

    def draw_crop(self, event):
        if self.cropping and self.display_image is not None:
            curr_x = self.canvas_original.canvasx(event.x)
            curr_y = self.canvas_original.canvasy(event.y)
            self.canvas_original.coords(self.rect, self.start_x, self.start_y, curr_x, curr_y)
            
            # Calculate scaling factors
            max_size = 500
            h, w = self.display_image.shape[:2]
            scale = min(max_size / w, max_size / h)
            display_w, display_h = int(w * scale), int(h * scale)
            scale_x = w / display_w
            scale_y = h / display_h
            
            # Convert canvas coordinates to image coordinates
            x1 = int(min(self.start_x, curr_x) * scale_x)
            y1 = int(min(self.start_y, curr_y) * scale_y)
            x2 = int(max(self.start_x, curr_x) * scale_x)
            y2 = int(max(self.start_y, curr_y) * scale_y)
            
            # Ensure coordinates are within image bounds
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)
            
            if x2 > x1 and y2 > y1:
                # Extract and display preview of cropped region
                crop_preview = self.display_image[y1:y2, x1:x2].copy()
                # Resize for display
                crop_h, crop_w = crop_preview.shape[:2]
                crop_scale = min(max_size / crop_w, max_size / crop_h)
                crop_display_size = (int(crop_w * crop_scale), int(crop_h * crop_scale))
                crop_display = cv2.resize(crop_preview, crop_display_size, interpolation=cv2.INTER_AREA)
                crop_display = cv2.cvtColor(crop_display, cv2.COLOR_BGR2RGB)
                self.cropped_photo = ImageTk.PhotoImage(image=Image.fromarray(crop_display))
                self.canvas_cropped.delete("all")
                self.canvas_cropped.create_image(0, 0, image=self.cropped_photo, anchor=tk.NW)
                self.canvas_cropped.config(scrollregion=(0, 0, crop_display_size[0], crop_display_size[1]))

    def end_crop(self, event):
        if self.cropping:
            self.cropping = False
            curr_x = self.canvas_original.canvasx(event.x)
            curr_y = self.canvas_original.canvasy(event.y)
            
            # Get displayed image dimensions
            max_size = 500
            h, w = self.display_image.shape[:2]
            scale = min(max_size / w, max_size / h)
            display_w, display_h = int(w * scale), int(h * scale)
            
            # Convert canvas coordinates to image coordinates
            scale_x = w / display_w
            scale_y = h / display_h
            x1 = int(min(self.start_x, curr_x) * scale_x)
            y1 = int(min(self.start_y, curr_y) * scale_y)
            x2 = int(max(self.start_x, curr_x) * scale_x)
            y2 = int(max(self.start_y, curr_y) * scale_y)
            
            # Ensure coordinates are within image bounds
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)
            
            if x2 > x1 and y2 > y1:
                self.cropped_image = self.display_image[y1:y2, x1:x2].copy()
                self.display_image = self.cropped_image.copy()
                self.add_to_history(self.display_image)
                self.update_display()
            self.canvas_original.delete(self.rect)
            self.rect = None

    def resize_image(self, event=None):
        if self.display_image is None:
            return
        scale = self.scale_slider.get() / 100
        self.scale_label.config(text=f"Resize Scale: {int(scale*100)}%")
        # Use cropped_image if available, else use display_image
        target_image = self.cropped_image if self.cropped_image is not None else self.display_image
        new_size = (int(target_image.shape[1] * scale), int(target_image.shape[0] * scale))
        self.display_image = cv2.resize(target_image, new_size, interpolation=cv2.INTER_AREA)
        self.cropped_image = self.display_image.copy()  # Update cropped_image
        self.add_to_history(self.display_image)
        self.update_display()

    def apply_grayscale(self):
        if self.display_image is None:
            return
        # Check if image is already grayscale
        if len(self.display_image.shape) == 2 or self.display_image.shape[2] == 1:
            return
        self.display_image = cv2.cvtColor(self.display_image, cv2.COLOR_BGR2GRAY)
        self.display_image = cv2.cvtColor(self.display_image, cv2.COLOR_GRAY2RGB)
        self.cropped_image = self.display_image.copy()  # Update cropped_image
        self.add_to_history(self.display_image)
        self.update_display()

    def apply_blur(self):
        if self.display_image is None:
            return
        self.display_image = cv2.GaussianBlur(self.display_image, (5, 5), 0)
        self.cropped_image = self.display_image.copy()  # Update cropped_image
        self.add_to_history(self.display_image)
        self.update_display()

    def save_image(self):
        if self.display_image is None:
            messagebox.showwarning("Warning", "No image to save")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".png", 
                                               filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")])
        if file_path:
            try:
                cv2.imwrite(file_path, self.display_image)
                messagebox.showinfo("Success", "Image saved successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image: {str(e)}")

    def add_to_history(self, image):
        self.history = self.history[:self.history_index + 1]
        self.history.append(image.copy())
        self.history_index += 1
        if len(self.history) > 10:  # Limit history size
            self.history.pop(0)
            self.history_index -= 1

    def undo(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.display_image = self.history[self.history_index].copy()
            self.cropped_image = self.display_image.copy()  # Update cropped_image
            self.update_display()

    def redo(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.display_image = self.history[self.history_index].copy()
            self.cropped_image = self.display_image.copy()  # Update cropped_image
            self.update_display()

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditorApp(root)
    root.mainloop()