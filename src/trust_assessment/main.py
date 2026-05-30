import tkinter as tk
from tkinter import messagebox
import random
from .utils.config import SENARIO_NAMES
from .models.participant import Participant
from .models.session import TestSession
from .models.response import QuestionResponse
from .services.video_service import VideoService
from .services.excel_service import ExcelService
from .ui.entry_window import EntryWindow
from .ui.video_player import VideoPlayer
from .ui.question_page import QuestionPage
from .ui.break_window import BreakWindow

class TrustAssessmentApp:
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("آزمون سنجش اعتماد کودکان")
        self.excel_service = ExcelService()
        self.session = None
        self.video_service = None
        self.current_scenario_index = 0
        self.scenario_order = []
        self.waiting_for_break = False
    
    def run(self):
        self.show_gender_selection()
        self.root.mainloop()
    
    def show_gender_selection(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.root.geometry("1024x768")
        
        main_frame = tk.Frame(self.root, bg="#2E7D64")
        main_frame.pack(expand=True)
        
        title = tk.Label(main_frame, text="آزمون سنجش اعتماد کودکان", 
                         font=("B Titr", 28), bg="#2E7D64", fg="white")
        title.pack(pady=50)
        
        btn_frame = tk.Frame(main_frame, bg="#2E7D64")
        btn_frame.pack(pady=40)
        
        girl_btn = tk.Button(btn_frame, text="دختران", command=lambda: self.start_test("girl"),
                             font=("B Nazanin", 20), bg="#FF69B4", fg="white", padx=40, pady=20)
        girl_btn.pack(side="left", padx=30)
        
        boy_btn = tk.Button(btn_frame, text="پسران", command=lambda: self.start_test("boy"),
                            font=("B Nazanin", 20), bg="#4169E1", fg="white", padx=40, pady=20)
        boy_btn.pack(side="left", padx=30)
    
    def start_test(self, gender: str):
        self.video_service = VideoService(gender)
        
        if not self.video_service.check_videos_exist():
            messagebox.showerror("خطا", "فایل‌های ویدیویی کامل نیستند.\nلطفاً ویدیوهای مورد نیاز را در پوشه مربوطه قرار دهید.")
            return
        
        self.scenario_order = self.video_service.get_random_order()
        
        for widget in self.root.winfo_children():
            widget.destroy()
        
        entry = EntryWindow(self.root, self.on_participant_submit, gender_selection=False)
    
    def on_participant_submit(self, participant: Participant):
        participant.gender = "girl" if self.video_service.gender == "girl" else "boy"
        participant.code = random.randint(1000, 9999)
        
        self.session = TestSession(
            participant=participant,
            scenario_order=self.scenario_order,
            current_scenario_index=0
        )
        
        self.current_scenario_index = 0
        self.waiting_for_break = False
        self.show_video()
    
    def show_video(self):
        if self.current_scenario_index >= len(self.scenario_order):
            self.finish_test()
            return
        
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.root.geometry("1024x768")
        
        scenario_name = self.scenario_order[self.current_scenario_index]
        video_path = self.video_service.get_video_path(scenario_name)
        
        if not video_path:
            messagebox.showerror("خطا", f"ویدیوی {scenario_name} یافت نشد")
            return
        
        player = VideoPlayer(self.root, video_path, self.on_video_complete)
        player.play()
    
    def on_video_complete(self):
        scenario_name = self.scenario_order[self.current_scenario_index]
        self.show_questions(scenario_name)
    
    def show_questions(self, scenario_name: str):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        question_page = QuestionPage(self.root, scenario_name, self.on_questions_complete)
    
    def on_questions_complete(self, scenario_name: str, responses: dict):
        for q_key, response in responses.items():
            self.session.add_response(scenario_name, response)
        
        self.current_scenario_index += 1
        
        if self.current_scenario_index == 4 and not self.waiting_for_break:
            self.waiting_for_break = True
            self.show_break()
        elif self.current_scenario_index >= len(self.scenario_order):
            self.finish_test()
        else:
            self.waiting_for_break = False
            self.show_video()
    
    def show_break(self):
        break_window = tk.Toplevel(self.root)
        break_window.title("استراحت")
        break_window.geometry("1024x768")
        
        def on_break_complete():
            break_window.destroy()
            self.waiting_for_break = False
            self.show_video()
        
        BreakWindow(break_window, on_break_complete)
    
    def finish_test(self):
        filename = self.excel_service.save_session(self.session)
        
        for widget in self.root.winfo_children():
            widget.destroy()
        
        finish_frame = tk.Frame(self.root, bg="#2E7D64")
        finish_frame.pack(expand=True)
        
        thanks = tk.Label(finish_frame, text="آزمایش با موفقیت انجام شد", 
                          font=("B Titr", 24), bg="#2E7D64", fg="white")
        thanks.pack(pady=50)
        
        info = tk.Label(finish_frame, text=f"داده‌های شما در فایل زیر ذخیره شد:\n{filename}", 
                        font=("B Nazanin", 14), bg="#2E7D64", fg="#FFD700")
        info.pack(pady=30)
        
        close_btn = tk.Button(finish_frame, text="خروج", command=self.root.quit,
                              font=("B Nazanin", 14), bg="#F44336", fg="white", padx=30, pady=10)
        close_btn.pack(pady=20)
        
        close_btn = tk.Button(finish_frame, text="ثبت مجدد", command=self.reset_and_restart,
                              font=("B Nazanin", 14), bg="#2196F3", fg="white", padx=30, pady=10)
        close_btn.pack(pady=10)
    
    def reset_and_restart(self):
        self.current_scenario_index = 0
        self.session = None
        self.waiting_for_break = False
        self.show_gender_selection()

def main():
    app = TrustAssessmentApp()
    app.run()

if __name__ == "__main__":
    main()