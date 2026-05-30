import cv2
import tkinter as tk
from PIL import Image, ImageTk
from typing import Optional

class VideoPlayer:
    
    def __init__(self, parent, video_path: str, on_complete=None):
        self.parent = parent
        self.video_path = video_path
        self.on_complete = on_complete
        self.cap = None
        self.canvas = None
        self.running = False
        self.after_id = None
    
    def play(self):
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            if self.on_complete:
                self.on_complete()
            return
        
        self.running = True
        self._create_ui()
        self._update_frame()
    
    def _create_ui(self):
        control_frame = tk.Frame(self.parent, bg="#2E7D64")
        control_frame.pack(side="bottom", pady=10)
        
        skip_btn = tk.Button(control_frame, text="رد کردن ویدیو", 
                             command=self._skip_video, font=("B Nazanin", 14), 
                             bg="#FF9800", fg="white", padx=20, pady=5)
        skip_btn.pack()
    
    def _update_frame(self):
        if not self.running:
            return
        
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (800, 600))
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            
            if self.canvas is None:
                self.canvas = tk.Canvas(self.parent, width=800, height=600, bg="black")
                self.canvas.pack(pady=20)
            
            self.canvas.delete("all")
            self.canvas.create_image(400, 300, image=imgtk, anchor=tk.CENTER)
            self.canvas.image = imgtk
            self.after_id = self.parent.after(33, self._update_frame)
        else:
            self.stop()
            if self.on_complete:
                self.on_complete()
    
    def _skip_video(self):
        self.stop()
        if self.on_complete:
            self.on_complete()
    
    def stop(self):
        self.running = False
        if self.after_id:
            self.parent.after_cancel(self.after_id)
        if self.cap:
            self.cap.release()
        if self.canvas:
            self.canvas.destroy()
            self.canvas = None