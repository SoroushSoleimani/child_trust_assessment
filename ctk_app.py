import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import random
import os
import pandas as pd
from datetime import datetime
import vlc
import time

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

SCORING_KEYS_FILE = os.path.join("data", "raw", "scoring_keys.xlsx")
DATA_DIR = os.path.join("data", "raw")
VIDEO_DIR = os.path.join("src", "trust_assessment", "assets", "videos")

SENARIO_NAMES = ["SEN1", "SEN2", "SEN3", "SEN4", "SEN5", "SEN6", "SEN7", "SEN8"]

QUESTIONS = [
    {"key": "niceness", "text": "به نظرت این پسر/دختر خوبیه؟"},
    {"key": "trust", "text": "به نظرت تو چقدر از حرفای این پسر/دختر رو قبول می‌کنی؟"},
    {"key": "self_disclosure", "text": "به نظرت تو رازهای خودتو به این پسر/دختر میگی؟"},
    {"key": "correctness", "text": "به نظرت چقدر از جوابای این پسر/دختر درست بود؟"},
]

ANSWER_OPTIONS = ["هیچکدوم", "فقط یه کوچولو", "نصفش", "بیشترش", "همه‌ش"]

class ModernTrustApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("آزمون سنجش اعتماد کودکان")
        self.root.geometry("1024x768")
        
        # تعریف فونت‌های جدید
        self.font_title = ctk.CTkFont(family="Yekan Bakh", size=32, weight="bold")
        self.font_subtitle = ctk.CTkFont(family="Yekan Bakh", size=24, weight="bold")
        self.font_button = ctk.CTkFont(family="Yekan Bakh", size=18, weight="bold")
        self.font_question = ctk.CTkFont(family="Sahel", size=16)
        self.font_option = ctk.CTkFont(family="Sahel", size=12)
        self.font_label = ctk.CTkFont(family="Sahel", size=14)
        
        self.gender = None
        self.participant = None
        self.scenario_order = []
        self.current_index = 0
        self.responses = {}
        self.break_completed = False
        self.break_timer_id = None
        self.vlc_instance = None
        self.vlc_player = None
        self.video_frame = None
        
        self.show_gender_selection()
    
    def clear_window(self):
        if self.break_timer_id:
            self.root.after_cancel(self.break_timer_id)
            self.break_timer_id = None
        if self.vlc_player:
            self.vlc_player.stop()
            self.vlc_player = None
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def show_gender_selection(self):
        self.clear_window()
        
        frame = ctk.CTkFrame(self.root)
        frame.pack(expand=True, fill="both", padx=40, pady=40)
        
        title = ctk.CTkLabel(frame, text="آزمون سنجش اعتماد کودکان", font=self.font_title)
        title.pack(pady=50)
        
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(pady=50)
        
        girl_btn = ctk.CTkButton(btn_frame, text="دختران", font=self.font_button,
                                  width=200, height=80, corner_radius=20, fg_color="#FF69B4",
                                  command=lambda: self.start_test("girl"))
        girl_btn.pack(side="left", padx=30)
        
        boy_btn = ctk.CTkButton(btn_frame, text="پسران", font=self.font_button,
                                width=200, height=80, corner_radius=20, fg_color="#4169E1",
                                command=lambda: self.start_test("boy"))
        boy_btn.pack(side="left", padx=30)
    
    def start_test(self, gender):
        self.gender = gender
        self.scenario_order = random.sample(SENARIO_NAMES, 8)
        self.current_index = 0
        self.responses = {}
        self.break_completed = False
        self.show_entry_form()
    
    def show_entry_form(self):
        self.clear_window()
        
        frame = ctk.CTkFrame(self.root)
        frame.pack(expand=True, fill="both", padx=40, pady=40)
        
        title = ctk.CTkLabel(frame, text="اطلاعات کودک", font=self.font_subtitle)
        title.pack(pady=30)
        
        name_entry = ctk.CTkEntry(frame, placeholder_text="نام و نام خانوادگی", width=400, font=self.font_label)
        name_entry.pack(pady=10)
        
        age_entry = ctk.CTkEntry(frame, placeholder_text="سن", width=200, font=self.font_label)
        age_entry.pack(pady=10)
        
        grade_var = tk.StringVar(value="اول")
        grade_frame = ctk.CTkFrame(frame, fg_color="transparent")
        grade_frame.pack(pady=10)
        ctk.CTkRadioButton(grade_frame, text="اول", variable=grade_var, value="اول", font=self.font_label).pack(side="left", padx=20)
        ctk.CTkRadioButton(grade_frame, text="دوم", variable=grade_var, value="دوم", font=self.font_label).pack(side="left", padx=20)
        
        def submit():
            if not name_entry.get() or not age_entry.get():
                messagebox.showerror("خطا", "لطفاً همه فیلدها را پر کنید")
                return
            
            self.participant = {
                "name": name_entry.get(),
                "age": int(age_entry.get()),
                "grade": grade_var.get(),
                "gender": self.gender,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.show_video()
        
        submit_btn = ctk.CTkButton(frame, text="شروع آزمایش", font=self.font_button,
                                    width=200, height=50, corner_radius=15, command=submit)
        submit_btn.pack(pady=30)
    
    def show_video(self):
        if self.current_index >= 8:
            self.save_to_excel()
            self.finish_test()
            return
        
        self.clear_window()
        
        frame = ctk.CTkFrame(self.root)
        frame.pack(expand=True, fill="both", padx=40, pady=40)
        
        scenario = self.scenario_order[self.current_index]
        
        title = ctk.CTkLabel(frame, text=f"ویدئو {scenario} - ویدئو شماره {self.current_index + 1} از 8", font=self.font_subtitle)
        title.pack(pady=20)
        
        self.video_frame = tk.Frame(frame, bg="black", width=640, height=480)
        self.video_frame.pack(pady=20)
        
        skip_btn = ctk.CTkButton(frame, text="رد کردن ویدئو", font=self.font_button,
                                  width=150, height=40, corner_radius=15, fg_color="#FF9800",
                                  command=self.skip_video)
        skip_btn.pack(pady=20)
        
        video_path = os.path.join(VIDEO_DIR, self.gender + "s", f"{scenario}.mp4")
        
        if os.path.exists(video_path):
            self.vlc_instance = vlc.Instance()
            self.vlc_player = self.vlc_instance.media_player_new()
            media = self.vlc_instance.media_new(video_path)
            self.vlc_player.set_media(media)
            self.vlc_player.set_hwnd(self.video_frame.winfo_id())
            self.vlc_player.play()
            self.check_video_end()
        else:
            messagebox.showerror("خطا", f"ویدئوی {scenario} یافت نشد")
            self.show_questions()
    
    def check_video_end(self):
        if self.vlc_player:
            state = self.vlc_player.get_state()
            if state == vlc.State.Ended:
                self.video_finished()
            else:
                self.root.after(500, self.check_video_end)
    
    def video_finished(self):
        if self.vlc_player:
            self.vlc_player.stop()
            self.vlc_player = None
        self.show_questions()
    
    def skip_video(self):
        if self.vlc_player:
            self.vlc_player.stop()
            self.vlc_player = None
        self.show_questions()
    
    def show_questions(self):
        if self.current_index >= 8:
            self.save_to_excel()
            self.finish_test()
            return
        
        if self.current_index == 4 and not self.break_completed:
            self.break_completed = True
            self.show_break()
            return
        
        self.clear_window()
        
        frame = ctk.CTkScrollableFrame(self.root)
        frame.pack(expand=True, fill="both", padx=40, pady=40)
        
        scenario = self.scenario_order[self.current_index]
        
        title = ctk.CTkLabel(frame, text=f"{scenario} - پاسخ به سوالات (سناریو {self.current_index + 1} از 8)", font=self.font_subtitle)
        title.pack(pady=20)
        
        answer_vars = {}
        
        for q in QUESTIONS:
            q_frame = ctk.CTkFrame(frame, corner_radius=15, border_width=2, border_color="#CCCCCC")
            q_frame.pack(fill="x", pady=10, padx=20)
            
            q_label = ctk.CTkLabel(q_frame, text=q["text"], font=self.font_question)
            q_label.pack(pady=10)
            
            answer_vars[q["key"]] = tk.IntVar(value=0)
            btn_frame = ctk.CTkFrame(q_frame, fg_color="transparent")
            btn_frame.pack(pady=10)
            
            for i, opt in enumerate(ANSWER_OPTIONS, 1):
                btn = ctk.CTkRadioButton(btn_frame, text=f"{i}- {opt}", variable=answer_vars[q["key"]], 
                                          value=i, font=self.font_option)
                btn.pack(side="left", padx=5)
        
        def submit():
            answers = {}
            for q in QUESTIONS:
                val = answer_vars[q["key"]].get()
                if val == 0:
                    messagebox.showwarning("هشدار", f"لطفاً به سوال '{q['text']}' پاسخ دهید")
                    return
                answers[q["key"]] = val
            
            self.responses[scenario] = answers
            self.current_index += 1
            self.show_video()
        
        submit_btn = ctk.CTkButton(frame, text="ادامه به ویدیوی بعدی", font=self.font_button,
                                    width=250, height=50, corner_radius=15, command=submit)
        submit_btn.pack(pady=30)
    
    def show_break(self):
        self.clear_window()
        
        frame = ctk.CTkFrame(self.root)
        frame.pack(expand=True, fill="both", padx=40, pady=40)
        
        title = ctk.CTkLabel(frame, text="زمان استراحت", font=self.font_title)
        title.pack(pady=40)
        
        message = ctk.CTkLabel(frame, text="می‌توانی کمی استراحت کنی", font=self.font_question)
        message.pack(pady=20)
        
        timer_label = ctk.CTkLabel(frame, text="زمان باقیمانده: 30 ثانیه", font=self.font_subtitle)
        timer_label.pack(pady=30)
        
        remaining = [30]
        
        def update_timer():
            if remaining[0] <= 0:
                self.show_video()
            else:
                remaining[0] -= 1
                timer_label.configure(text=f"زمان باقیمانده: {remaining[0]} ثانیه")
                self.break_timer_id = self.root.after(1000, update_timer)
        
        def skip():
            if self.break_timer_id:
                self.root.after_cancel(self.break_timer_id)
                self.break_timer_id = None
            self.show_video()
        
        skip_btn = ctk.CTkButton(frame, text="رد کردن استراحت", font=self.font_button,
                                  width=200, height=40, corner_radius=15, fg_color="#FF9800", command=skip)
        skip_btn.pack(pady=20)
        
        update_timer()
    
    def get_next_row_number(self):
        if not os.path.exists(SCORING_KEYS_FILE):
            return 1
        try:
            df = pd.read_excel(SCORING_KEYS_FILE, sheet_name='Sheet1')
            if df.empty or 'ردیف' not in df.columns:
                return 1
            max_row = df['ردیف'].max()
            if pd.isna(max_row):
                return 1
            return int(max_row) + 1
        except:
            return 1
    
    def save_to_excel(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        
        if len(self.responses) != 8:
            messagebox.showerror("خطا", f"تعداد پاسخ‌ها {len(self.responses)} است، باید 8 باشد. ذخیره نشد.")
            return
        
        row_number = self.get_next_row_number()
        
        if os.path.exists(SCORING_KEYS_FILE):
            try:
                sheet1_df = pd.read_excel(SCORING_KEYS_FILE, sheet_name='Sheet1')
            except:
                sheet1_df = pd.DataFrame()
            try:
                sheet3_df = pd.read_excel(SCORING_KEYS_FILE, sheet_name='Sheet3')
            except:
                sheet3_df = pd.DataFrame()
        else:
            sheet1_df = pd.DataFrame()
            sheet3_df = pd.DataFrame()
        
        row1 = {
            "ردیف": row_number,
            "نام": self.participant["name"],
            "سن": self.participant["age"],
            "کلاس": self.participant["grade"],
        }
        
        persian_nums = ["اول", "دوم", "سوم", "چهارم", "پنجم", "ششم", "هفتم", "هشتم"]
        for i, scenario in enumerate(self.scenario_order):
            row1[f"نمایش {persian_nums[i]}"] = scenario
        
        for scenario in self.scenario_order:
            if scenario in self.responses:
                ans = self.responses[scenario]
                row1[f"{scenario}-NIC"] = ans.get("niceness", "")
                row1[f"{scenario}-T"] = ans.get("trust", "")
                row1[f"{scenario}-SD"] = ans.get("self_disclosure", "")
                row1[f"{scenario}-CO"] = ans.get("correctness", "")
        
        sheet1_df = pd.concat([sheet1_df, pd.DataFrame([row1])], ignore_index=True)
        
        order_str = ''.join([s.replace('SEN', '') for s in self.scenario_order])
        
        total_scores = {
            "niceness": {"mistrust": 0, "trust": 0, "gullibility": 0},
            "trust": {"mistrust": 0, "trust": 0, "gullibility": 0},
            "self_disclosure": {"mistrust": 0, "trust": 0, "gullibility": 0},
            "correctness": {"mistrust": 0, "trust": 0, "gullibility": 0},
        }
        
        for scenario, answers in self.responses.items():
            for q_type, answer in answers.items():
                scores = self.get_scores_from_keys(scenario, answer)
                if q_type in total_scores:
                    total_scores[q_type]["mistrust"] += scores.get("mistrust", 0)
                    total_scores[q_type]["trust"] += scores.get("trust", 0)
                    total_scores[q_type]["gullibility"] += scores.get("gullibility", 0)
        
        row3 = {
            "ردیف": row_number,
            "نام": self.participant["name"],
            "سن": self.participant["age"],
            "کلاس": self.participant["grade"],
            "ترتیب نمایش‌ها": order_str,
            "بی‌اعتمادی(خوب بودن)": total_scores["niceness"]["mistrust"],
            "اعتمادمعرفتی(خوب بودن)": total_scores["niceness"]["trust"],
            "ساده لوحی(خوب بودن)": total_scores["niceness"]["gullibility"],
            "بی‌اعتمادی(اعتماد)": total_scores["trust"]["mistrust"],
            "اعتمادمعرفتی(اعتماد)": total_scores["trust"]["trust"],
            "ساده لوحی(اعتماد)": total_scores["trust"]["gullibility"],
            "بی‌اعتمادی(خودافشایی)": total_scores["self_disclosure"]["mistrust"],
            "اعتمادمعرفتی(خودافشایی)": total_scores["self_disclosure"]["trust"],
            "ساده لوحی(خودافشایی)": total_scores["self_disclosure"]["gullibility"],
            "بی‌اعتمادی(درست بودن)": total_scores["correctness"]["mistrust"],
            "اعتمادمعرفتی(درست بودن)": total_scores["correctness"]["trust"],
            "ساده لوحی(درست بودن)": total_scores["correctness"]["gullibility"],
            "جمع بی اعتمادی": sum(s["mistrust"] for s in total_scores.values()),
            "جمع اعتماد معرفتی": sum(s["trust"] for s in total_scores.values()),
            "جمع ساده لوحی": sum(s["gullibility"] for s in total_scores.values()),
        }
        
        sheet3_df = pd.concat([sheet3_df, pd.DataFrame([row3])], ignore_index=True)
        
        try:
            scoring_keys_df = pd.read_excel(SCORING_KEYS_FILE, sheet_name='Sheet2') if os.path.exists(SCORING_KEYS_FILE) else pd.DataFrame()
        except:
            scoring_keys_df = pd.DataFrame()
        
        with pd.ExcelWriter(SCORING_KEYS_FILE, engine='openpyxl', mode='w') as writer:
            sheet1_df.to_excel(writer, sheet_name='Sheet1', index=False)
            scoring_keys_df.to_excel(writer, sheet_name='Sheet2', index=False)
            sheet3_df.to_excel(writer, sheet_name='Sheet3', index=False)
    
    def get_scores_from_keys(self, scenario, answer):
        if not os.path.exists(SCORING_KEYS_FILE):
            return {"mistrust": 0, "trust": 0, "gullibility": 0}
        try:
            df = pd.read_excel(SCORING_KEYS_FILE, sheet_name='Sheet2')
            mask = (df["سناریو"] == scenario) & (df["شماره گزینه"] == answer)
            filtered = df[mask]
            if len(filtered) > 0:
                row = filtered.iloc[0]
                return {
                    "mistrust": int(row.get("بی اعتمادی", 0)),
                    "trust": int(row.get("اعتماد", 0)),
                    "gullibility": int(row.get("ساده لوحی", 0))
                }
        except Exception as e:
            print(f"Error getting scores: {e}")
        return {"mistrust": 0, "trust": 0, "gullibility": 0}
    
    def finish_test(self):
        self.clear_window()
        
        frame = ctk.CTkFrame(self.root)
        frame.pack(expand=True, fill="both", padx=40, pady=40)
        
        thanks = ctk.CTkLabel(frame, text="آزمایش با موفقیت انجام شد!", font=self.font_title, text_color="green")
        thanks.pack(pady=50)
        
        info = ctk.CTkLabel(frame, text=f"داده‌های شما در فایل:\n{SCORING_KEYS_FILE} ذخیره شد\n\nتعداد سناریوهای ثبت شده: {len(self.responses)} از 8", font=self.font_label)
        info.pack(pady=30)
        
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        close_btn = ctk.CTkButton(btn_frame, text="خروج", font=self.font_button,
                                   width=150, height=40, corner_radius=15, fg_color="#F44336", command=self.root.quit)
        close_btn.pack(side="left", padx=20)
        
        new_btn = ctk.CTkButton(btn_frame, text="آزمون جدید", font=self.font_button,
                                 width=150, height=40, corner_radius=15, fg_color="#2196F3", command=self.restart)
        new_btn.pack(side="left", padx=20)
    
    def restart(self):
        if self.vlc_player:
            self.vlc_player.stop()
            self.vlc_player = None
        self.gender = None
        self.participant = None
        self.scenario_order = []
        self.current_index = 0
        self.responses = {}
        self.break_completed = False
        if self.break_timer_id:
            self.root.after_cancel(self.break_timer_id)
            self.break_timer_id = None
        self.show_gender_selection()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ModernTrustApp()
    app.run()