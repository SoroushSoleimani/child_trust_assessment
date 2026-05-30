import tkinter as tk
from ..utils.config import WINDOW_WIDTH, WINDOW_HEIGHT, BACKGROUND_COLOR, BREAK_DURATION_SECONDS

class BreakWindow:
    
    def __init__(self, parent, on_complete):
        self.parent = parent
        self.on_complete = on_complete
        self.remaining = BREAK_DURATION_SECONDS
        self.after_id = None
        self.skipped = False
        
        self.parent.title("زمان استراحت")
        self.parent.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.parent.configure(bg=BACKGROUND_COLOR)
        
        self._create_widgets()
        self._start_timer()
    
    def _create_widgets(self):
        main_frame = tk.Frame(self.parent, bg=BACKGROUND_COLOR)
        main_frame.pack(expand=True)
        
        title = tk.Label(main_frame, text="زمان استراحت", 
                         font=("B Titr", 28), bg=BACKGROUND_COLOR, fg="white")
        title.pack(pady=50)
        
        message = tk.Label(main_frame, text="می‌توانی کمی استراحت کنی", 
                           font=("B Nazanin", 18), bg=BACKGROUND_COLOR, fg="#FFD700")
        message.pack(pady=20)
        
        self.timer_label = tk.Label(main_frame, text=f"زمان باقی‌مانده: {self.remaining} ثانیه", 
                                     font=("B Nazanin", 24), bg=BACKGROUND_COLOR, fg="white")
        self.timer_label.pack(pady=40)
        
        skip_btn = tk.Button(main_frame, text="رد کردن استراحت", 
                             command=self._skip, font=("B Nazanin", 14), 
                             bg="#FF9800", fg="white", padx=30, pady=10)
        skip_btn.pack(pady=20)
    
    def _start_timer(self):
        self._update_timer()
    
    def _update_timer(self):
        if self.skipped:
            return
        
        if self.remaining <= 0:
            self._finish()
        else:
            self.timer_label.config(text=f"زمان باقی‌مانده: {self.remaining} ثانیه")
            self.remaining -= 1
            self.after_id = self.parent.after(1000, self._update_timer)
    
    def _skip(self):
        if self.skipped:
            return
        
        self.skipped = True
        if self.after_id:
            self.parent.after_cancel(self.after_id)
        self._finish()
    
    def _finish(self):
        self.parent.destroy()
        self.on_complete()