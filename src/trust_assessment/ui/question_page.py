import tkinter as tk
from tkinter import messagebox
import time
from ..utils.config import WINDOW_WIDTH, WINDOW_HEIGHT, BACKGROUND_COLOR, QUESTIONS, ANSWER_OPTIONS
from ..models.response import QuestionResponse

class QuestionPage:
    
    def __init__(self, parent, scenario_name: str, on_complete):
        self.parent = parent
        self.scenario_name = scenario_name
        self.on_complete = on_complete
        self.responses = {}
        self.start_times = {}
        self.buttons = {}
        
        self.parent.title(f"پرسش‌ها - {scenario_name}")
        self.parent.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.parent.configure(bg=BACKGROUND_COLOR)
        
        self._create_widgets()
    
    def _create_widgets(self):
        main_frame = tk.Frame(self.parent, bg=BACKGROUND_COLOR)
        main_frame.pack(expand=True, fill="both")
        
        scenario_label = tk.Label(main_frame, text=f"سناریو: {self.scenario_name}", 
                                   font=("B Titr", 18), bg=BACKGROUND_COLOR, fg="white")
        scenario_label.pack(pady=20)
        
        self.question_frames = {}
        
        for idx, q in enumerate(QUESTIONS):
            q_frame = tk.LabelFrame(main_frame, text=q["text"], font=("B Nazanin", 14), 
                                     bg="white", fg="black", padx=20, pady=10)
            q_frame.pack(pady=10, padx=50, fill="x")
            
            self.question_frames[q["key"]] = q_frame
            self.start_times[q["key"]] = None
            
            btn_frame = tk.Frame(q_frame, bg="white")
            btn_frame.pack(pady=10)
            
            self.buttons[q["key"]] = []
            for opt_idx, opt_text in enumerate(ANSWER_OPTIONS):
                btn = tk.Button(btn_frame, text=f"{opt_idx+1} - {opt_text}", 
                               command=lambda k=q["key"], v=opt_idx+1: self._answer_selected(k, v),
                               font=("B Nazanin", 12), bg="#E0E0E0", padx=15, pady=5)
                btn.pack(side="left", padx=5)
                self.buttons[q["key"]].append(btn)
        
        self.submit_btn = tk.Button(main_frame, text="ادامه به ویدیوی بعدی", 
                                    command=self._submit_all, font=("B Nazanin", 14), 
                                    bg="#4CAF50", fg="white", padx=30, pady=10, state="disabled")
        self.submit_btn.pack(pady=20)
    
    def _answer_selected(self, question_key: str, value: int):
        if self.start_times[question_key] is None:
            self.start_times[question_key] = int(time.time() * 1000)
        
        response_time = int(time.time() * 1000) - self.start_times[question_key]
        
        self.responses[question_key] = QuestionResponse(
            question_key=question_key,
            answer_value=value,
            response_time_ms=response_time
        )
        
        for btn in self.buttons[question_key]:
            btn.config(bg="#E0E0E0")
        for btn in self.buttons[question_key]:
            if btn.cget("text").startswith(str(value)):
                btn.config(bg="#4CAF50", fg="white")
                break
        
        if len(self.responses) == 4:
            self.submit_btn.config(state="normal")
    
    def _submit_all(self):
        if len(self.responses) != 4:
            messagebox.showwarning("هشدار", "لطفاً به همه سوالات پاسخ دهید")
            return
        
        self.on_complete(self.scenario_name, self.responses)