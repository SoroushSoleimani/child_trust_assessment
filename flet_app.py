import flet as ft
import pandas as pd
import os
import random
import time
from datetime import datetime

SCORING_KEYS_FILE = os.path.join("data", "raw", "scoring_keys.xlsx")
DATA_DIR = os.path.join("data", "raw")
VIDEO_DIR = os.path.join("src", "trust_assessment", "assets", "videos")

SENARIO_NAMES = ["SEN1", "SEN2", "SEN3", "SEN4", "SEN5", "SEN6", "SEN7", "SEN8"]

QUESTIONS = [
    {"key": "correctness", "text": "به نظرت چقدر از جوابای این پسر/دختر درست بود؟"},
    {"key": "niceness", "text": "به نظرات این پسر/دختر خوبیه؟"},
    {"key": "trust", "text": "به نظرت تو چقدر از حرفای این پسر/دختر رو قبول می‌کنی؟"},
    {"key": "self_disclosure", "text": "به نظرات تو رازهای خودتو به این پسر/دختر میگی؟"},
]

ANSWER_OPTIONS = ["هیچکدوم", "فقط یه کوچولو", "نصفش", "بیشترش", "همه‌ش"]

class TrustApp:
    def __init__(self):
        self.page = None
        self.gender = None
        self.participant = None
        self.scenario_order = []
        self.current_index = 0
        self.responses = {}
        self.waiting_for_break = False
    
    def run(self, page: ft.Page):
        self.page = page
        page.title = "آزمون سنجش اعتماد کودکان"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.bgcolor = ft.Colors.WHITE
        page.window_width = 1024
        page.window_height = 768
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        
        self.show_gender_selection()
        page.update()
    
    def show_gender_selection(self):
        self.page.clean()
        
        title = ft.Text("آزمون سنجش اعتماد کودکان", size=40, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800)
        
        girl_btn = ft.ElevatedButton(
            content=ft.Text("دختران", size=28, weight=ft.FontWeight.BOLD),
            on_click=lambda e: self.start_test("girl"),
            width=250, height=120,
            style=ft.ButtonStyle(bgcolor=ft.Colors.PINK_400, color=ft.Colors.WHITE)
        )
        
        boy_btn = ft.ElevatedButton(
            content=ft.Text("پسران", size=28, weight=ft.FontWeight.BOLD),
            on_click=lambda e: self.start_test("boy"),
            width=250, height=120,
            style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_400, color=ft.Colors.WHITE)
        )
        
        self.page.add(
            ft.Column([
                ft.Container(height=100),
                title,
                ft.Container(height=80),
                ft.Row([girl_btn, boy_btn], alignment=ft.MainAxisAlignment.CENTER, spacing=60),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )
    
    def start_test(self, gender):
        self.gender = gender
        self.scenario_order = random.sample(SENARIO_NAMES, 8)
        self.current_index = 0
        self.responses = {}
        self.waiting_for_break = False
        self.show_entry_form()
    
    def show_entry_form(self):
        self.page.clean()
        
        name_field = ft.TextField(label="نام و نام خانوادگی", width=400, text_align=ft.TextAlign.RIGHT)
        age_field = ft.TextField(label="سن", width=200, text_align=ft.TextAlign.RIGHT, input_filter=ft.NumbersOnlyInputFilter())
        grade_field = ft.Dropdown(label="پایه تحصیلی", width=200, options=[
            ft.dropdown.Option("اول"), ft.dropdown.Option("دوم")
        ])
        
        def submit(e):
            if not name_field.value or not age_field.value or not grade_field.value:
                return
            self.participant = {
                "name": name_field.value,
                "age": int(age_field.value),
                "grade": grade_field.value,
                "gender": self.gender,
                "code": random.randint(1000, 9999),
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.show_video()
        
        submit_btn = ft.ElevatedButton("شروع آزمایش", on_click=submit, width=200)
        
        self.page.add(
            ft.Column([
                ft.Container(height=100),
                ft.Text("اطلاعات کودک", size=30, weight=ft.FontWeight.BOLD),
                ft.Container(height=30),
                name_field,
                ft.Container(height=15),
                ft.Row([age_field, grade_field], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(height=30),
                submit_btn,
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )
    
    def show_video(self):
        if self.current_index >= 8:
            self.finish_test()
            return
        
        if self.current_index == 4 and not self.waiting_for_break:
            self.waiting_for_break = True
            self.show_break()
            return
        
        self.page.clean()
        
        scenario = self.scenario_order[self.current_index]
        video_path = os.path.join(VIDEO_DIR, self.gender + "s", f"{scenario}.mp4")
        
        video_text = ft.Text(f"در حال پخش ویدئو {scenario}...", size=24)
        
        def next_video(e):
            self.current_index += 1
            self.show_video()
        
        next_btn = ft.ElevatedButton("رد کردن ویدئو", on_click=next_video)
        
        self.page.add(
            ft.Column([
                ft.Container(height=150),
                video_text,
                ft.Container(height=50),
                next_btn,
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )
        
        # شبیه‌سازی پخش ویدئو (در نسخه واقعی باید از Video Player استفاده کنید)
        self.page.update()
    
    def show_break(self):
        self.page.clean()
        
        timer_text = ft.Text("زمان باقیمانده: 30", size=30)
        
        def skip(e):
            self.waiting_for_break = False
            self.show_video()
        
        def update_timer(remaining):
            if remaining <= 0:
                self.waiting_for_break = False
                self.show_video()
            else:
                timer_text.value = f"زمان باقیمانده: {remaining}"
                self.page.update()
                self.page.after(1000, lambda: update_timer(remaining - 1))
        
        skip_btn = ft.ElevatedButton("رد کردن استراحت", on_click=skip)
        
        self.page.add(
            ft.Column([
                ft.Container(height=150),
                ft.Text("زمان استراحت", size=36, weight=ft.FontWeight.BOLD),
                ft.Container(height=30),
                timer_text,
                ft.Container(height=30),
                skip_btn,
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )
        
        update_timer(30)
    
    def finish_test(self):
        self.page.clean()
        
        filename = os.path.join(DATA_DIR, f"result_{self.participant['code']}.xlsx")
        os.makedirs(DATA_DIR, exist_ok=True)
        
        df = pd.DataFrame([self.participant])
        df.to_excel(filename, index=False)
        
        self.page.add(
            ft.Column([
                ft.Container(height=150),
                ft.Text("آزمایش با موفقیت انجام شد!", size=36, color=ft.Colors.GREEN, weight=ft.FontWeight.BOLD),
                ft.Container(height=30),
                ft.Text(f"فایل ذخیره شد: {filename}", size=16),
                ft.Container(height=50),
                ft.ElevatedButton("پایان", on_click=lambda e: self.page.window_close(), width=200),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )

def main():
    ft.app(target=TrustApp().run)

if __name__ == "__main__":
    main()