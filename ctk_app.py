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

ANSWER_OPTIONS = [
    "گزینه 1 ( 😡 هیچکدوم از حرفاشو قبول نمی‌کنم )",
    "گزینه 2 ( 😐 فقط یه کوچولو از حرفاشو قبول می‌کنم )",
    "گزینه 3 ( 😌 نصف حرفاشو قبول می‌کنم )",
    "گزینه 4 ( 😊 بیشتر حرفاشو قبول می‌کنم )",
    "گزینه 5 ( 😍 همه‌ی حرفاشو قبول می‌کنم )",
]

class ModernTrustApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("آزمون سنجش اعتماد کودکان")
        self.root.geometry("1024x768")
        
        # Fonts
        self.font_title = ctk.CTkFont(family="Yekan Bakh", size=32, weight="bold")
        self.font_subtitle = ctk.CTkFont(family="Yekan Bakh", size=24, weight="bold")
        self.font_button = ctk.CTkFont(family="Yekan Bakh", size=18, weight="bold")
        self.font_question = ctk.CTkFont(family="Sahel", size=32, weight="bold")
        self.font_option_text = ctk.CTkFont(family="Sahel", size=22)
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
        self.is_playing = False
        
        self.current_question_index = 0
        self.current_scenario = None
        self.temp_answers = {}
        
        self.gold_standard_options = {}
        self.load_gold_standards()
        
        self.show_gender_selection()
    
    def load_gold_standards(self):
        if not os.path.exists(SCORING_KEYS_FILE):
            return
        try:
            df = pd.read_excel(SCORING_KEYS_FILE, sheet_name='Sheet2')
            df = df.dropna(subset=['سناریو', 'شماره گزینه'])
            for _, row in df.iterrows():
                scenario = str(row["سناریو"]).strip()
                opt_val = str(row["شماره گزینه"]).strip()
                if '*' in opt_val:
                    num = int(opt_val.replace('*', '').strip())
                    self.gold_standard_options[scenario] = num
        except Exception as e:
            print(f"خطا در بارگذاری گزینه‌های طلایی: {e}")
    
    def get_gold_standard(self, scenario):
        return self.gold_standard_options.get(scenario, None)
    
    def set_background_color(self):
        if self.gender == "girl":
            self.root.configure(fg_color="#FFCDD2")  # صورتی ملایم
        elif self.gender == "boy":
            self.root.configure(fg_color="#BBDEFB")  # آبی ملایم
        else:
            self.root.configure(fg_color="#E3F2FD")  # آبی بسیار روشن برای صفحه اول
    
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
        self.root.configure(fg_color="#E3F2FD")
        
        frame = ctk.CTkFrame(self.root, fg_color="transparent")
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
        self.set_background_color()
        self.scenario_order = random.sample(SENARIO_NAMES, 8)
        self.current_index = 0
        self.responses = {}
        self.break_completed = False
        self.show_entry_form()
    
    def show_entry_form(self):
        self.clear_window()
        self.set_background_color()
        
        frame = ctk.CTkFrame(self.root, fg_color="transparent")
        frame.pack(expand=True, fill="both", padx=40, pady=40)
        
        title = ctk.CTkLabel(frame, text="اطلاعات کودک", font=self.font_subtitle)
        title.pack(pady=30)
        
        name_entry = ctk.CTkEntry(frame, placeholder_text="نام و نام خانوادگی", width=400, font=self.font_label)
        name_entry.pack(pady=10)
        
        age_entry = ctk.CTkEntry(frame, placeholder_text="سن", width=200, font=self.font_label)
        age_entry.pack(pady=10)
        
        grades = ["اول", "دوم", "سوم", "چهارم", "پنجم", "ششم"]
        grade_combo = ctk.CTkComboBox(frame, values=grades, font=self.font_label, width=200)
        grade_combo.pack(pady=10)
        grade_combo.set("اول")
        
        def submit():
            if not name_entry.get() or not age_entry.get():
                messagebox.showerror("خطا", "لطفاً همه فیلدها را پر کنید")
                return
            
            self.participant = {
                "name": name_entry.get(),
                "age": int(age_entry.get()),
                "grade": grade_combo.get(),
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
        self.set_background_color()
        
        frame = ctk.CTkFrame(self.root, fg_color="transparent")
        frame.pack(expand=True, fill="both", padx=40, pady=40)
        
        scenario = self.scenario_order[self.current_index]
        
        title = ctk.CTkLabel(frame, text=f"ویدئو {scenario} - ویدئو شماره {self.current_index + 1} از 8", font=self.font_subtitle)
        title.pack(pady=20)
        
        self.video_frame = tk.Frame(frame, bg="black", width=900, height=600)
        self.video_frame.pack(pady=10)
        self.video_frame.pack_propagate(False)
        
        control_frame = ctk.CTkFrame(frame, fg_color="transparent")
        control_frame.pack(pady=10)
        
        self.pause_play_btn = ctk.CTkButton(control_frame, text="⏸️ توقف", font=self.font_button,
                                            width=100, height=40, corner_radius=15, fg_color="#555555",
                                            command=self.toggle_pause)
        self.pause_play_btn.pack(side="left", padx=10)
        
        rewind_btn = ctk.CTkButton(control_frame, text="⏪ 15 ثانیه", font=self.font_button,
                                   width=120, height=40, corner_radius=15, fg_color="#FF9800",
                                   command=self.rewind_15)
        rewind_btn.pack(side="left", padx=10)
        
        skip_btn = ctk.CTkButton(control_frame, text="رد کردن ویدئو", font=self.font_button,
                                 width=120, height=40, corner_radius=15, fg_color="#F44336",
                                 command=self.skip_video)
        skip_btn.pack(side="left", padx=10)
        
        video_path = os.path.join(VIDEO_DIR, self.gender + "s", f"{scenario}.mp4")
        
        if os.path.exists(video_path):
            self.vlc_instance = vlc.Instance()
            self.vlc_player = self.vlc_instance.media_player_new()
            media = self.vlc_instance.media_new(video_path)
            self.vlc_player.set_media(media)
            self.vlc_player.set_hwnd(self.video_frame.winfo_id())
            self.vlc_player.play()
            self.is_playing = True
            self.check_video_end()
        else:
            messagebox.showerror("خطا", f"ویدئوی {scenario} یافت نشد")
            self.show_questions()
    
    def toggle_pause(self):
        if not self.vlc_player:
            return
        if self.is_playing:
            self.vlc_player.pause()
            self.is_playing = False
            self.pause_play_btn.configure(text="▶️ شروع")
        else:
            self.vlc_player.play()
            self.is_playing = True
            self.pause_play_btn.configure(text="⏸️ توقف")
    
    def rewind_15(self):
        if not self.vlc_player:
            return
        current_time = self.vlc_player.get_time()
        new_time = max(0, current_time - 15000)
        self.vlc_player.set_time(new_time)
        if not self.is_playing:
            self.vlc_player.play()
            self.is_playing = True
            self.pause_play_btn.configure(text="⏸️ توقف")
    
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
        self.is_playing = False
        self.show_questions()
    
    def skip_video(self):
        if self.vlc_player:
            self.vlc_player.stop()
            self.vlc_player = None
        self.is_playing = False
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
        
        self.current_scenario = self.scenario_order[self.current_index]
        self.current_question_index = 0
        self.temp_answers = {}
        self.display_question()
    
    def display_question(self):
        if self.current_question_index >= len(QUESTIONS):
            self.responses[self.current_scenario] = self.temp_answers
            self.current_index += 1
            self.show_video()
            return
        
        self.clear_window()
        self.set_background_color()
        
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=40, pady=40)
        
        q_number = self.current_question_index + 1
        q_data = QUESTIONS[self.current_question_index]
        
        header = ctk.CTkLabel(main_frame, text=f"{self.current_scenario} - سوال {q_number} از 4", 
                              font=self.font_subtitle)
        header.pack(pady=20)
        
        question_text = ctk.CTkLabel(
            main_frame,
            text=q_data["text"],
            font=self.font_question,
            justify="right",
            anchor="e",
            wraplength=900
        )
        question_text.pack(pady=40, padx=30, anchor="e")
        
        gold_opt = self.get_gold_standard(self.current_scenario)
        answer_var = tk.IntVar(value=0)
        
        options_frame = ctk.CTkScrollableFrame(main_frame, fg_color="white", border_width=2, border_color="#CCCCCC")
        options_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        for i, opt_text in enumerate(ANSWER_OPTIONS, 1):
            opt_container = ctk.CTkFrame(options_frame, fg_color="transparent")
            opt_container.pack(fill="x", pady=8, padx=10)
            
            radio = ctk.CTkRadioButton(
                opt_container,
                variable=answer_var,
                value=i,
                text="",
                fg_color=("#3B8ED0", "#1F6AA5") if self.gender == "boy" else ("#E91E63", "#C2185B"),
                hover_color=("#3B8ED0", "#1F6AA5") if self.gender == "boy" else ("#E91E63", "#C2185B"),
                border_color="#666666"
            )
            radio.pack(side="right", padx=(10, 5))
            
            display_text = opt_text
            if i == gold_opt:
                display_text = f"{opt_text} ⭐"
            
            label = ctk.CTkLabel(
                opt_container,
                text=display_text,
                font=self.font_option_text,
                anchor="e",
                justify="right",
                wraplength=700,
                text_color="#000000"
            )
            label.pack(side="right", fill="x", expand=True, padx=(5, 10))
            
            label.bind("<Button-1>", lambda e, rb=radio, var=answer_var, val=i: (var.set(val), rb.select()))
            opt_container.bind("<Button-1>", lambda e, rb=radio, var=answer_var, val=i: (var.set(val), rb.select()))
        
        def next_question():
            val = answer_var.get()
            if val == 0:
                messagebox.showwarning("هشدار", "لطفاً یک گزینه را انتخاب کنید")
                return
            self.temp_answers[q_data["key"]] = val
            self.current_question_index += 1
            self.display_question()
        
        next_btn = ctk.CTkButton(main_frame, text="سوال بعدی", font=self.font_button,
                                 width=200, height=50, corner_radius=15, command=next_question)
        next_btn.pack(pady=40)
    
    def show_break(self):
        self.clear_window()
        self.set_background_color()
        
        frame = ctk.CTkFrame(self.root, fg_color="transparent")
        frame.pack(expand=True, fill="both", padx=40, pady=40)
        
        title = ctk.CTkLabel(frame, text="زمان استراحت", font=self.font_title)
        title.pack(pady=40)
        
        message = ctk.CTkLabel(frame, text="می‌توانی کمی استراحت کنی", font=self.font_question)
        message.pack(pady=20)
        
        timer_label = ctk.CTkLabel(frame, text="زمان باقیمانده: 30 ثانیه", font=self.font_subtitle)
        timer_label.pack(pady=30)
        
        remaining = 30
        
        def update_timer():
            nonlocal remaining
            if remaining <= 0:
                self.show_video()
            else:
                remaining -= 1
                timer_label.configure(text=f"زمان باقیمانده: {remaining} ثانیه")
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
    
    def get_scores_from_keys(self, scenario, answer):
        if not os.path.exists(SCORING_KEYS_FILE):
            return {"mistrust": 0, "trust": 0, "gullibility": 0}
        try:
            df = pd.read_excel(SCORING_KEYS_FILE, sheet_name='Sheet2')
            df = df.dropna(subset=['سناریو', 'شماره گزینه'])
            def clean_option(val):
                if pd.isna(val):
                    return None
                s = str(val).strip()
                s = s.replace('*', '').strip()
                try:
                    return int(s)
                except:
                    return None
            df['شماره گزینه_clean'] = df['شماره گزینه'].apply(clean_option)
            df = df.dropna(subset=['شماره گزینه_clean'])
            mask = (df["سناریو"] == scenario) & (df['شماره گزینه_clean'] == answer)
            filtered = df[mask]
            if len(filtered) > 0:
                row = filtered.iloc[0]
                return {
                    "mistrust": int(row.get("بی اعتمادی", 0)),
                    "trust": int(row.get("اعتماد", 0)),
                    "gullibility": int(row.get("ساده لوحی", 0))
                }
        except Exception as e:
            print(f"Error in get_scores_from_keys: {e}")
        return {"mistrust": 0, "trust": 0, "gullibility": 0}
    
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
        
        print("=== نتایج محاسبه شده ===")
        print(f"جمع بی اعتمادی: {row3['جمع بی اعتمادی']}")
        print(f"جمع اعتماد معرفتی: {row3['جمع اعتماد معرفتی']}")
        print(f"جمع ساده لوحی: {row3['جمع ساده لوحی']}")
        
        sheet3_df = pd.concat([sheet3_df, pd.DataFrame([row3])], ignore_index=True)
        
        try:
            if os.path.exists(SCORING_KEYS_FILE):
                scoring_keys_df = pd.read_excel(SCORING_KEYS_FILE, sheet_name='Sheet2')
            else:
                scoring_keys_df = pd.DataFrame()
        except:
            scoring_keys_df = pd.DataFrame()
        
        try:
            with pd.ExcelWriter(SCORING_KEYS_FILE, engine='openpyxl', mode='w') as writer:
                sheet1_df.to_excel(writer, sheet_name='Sheet1', index=False)
                scoring_keys_df.to_excel(writer, sheet_name='Sheet2', index=False)
                sheet3_df.to_excel(writer, sheet_name='Sheet3', index=False)
            print("فایل با موفقیت ذخیره شد.")
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در ذخیره فایل Excel: {str(e)}")
    
    def finish_test(self):
        self.clear_window()
        
        frame = ctk.CTkFrame(self.root, fg_color="transparent")
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