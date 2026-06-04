import flet as ft
import pandas as pd
import os
import random
import time
from datetime import datetime

# ============================================================================
# TRUST ASSESSMENT APPLICATION (FLET VERSION)
# ============================================================================
# This module implements a cross-platform GUI application using the Flet framework
# (which builds on Flutter) for the Child Trust Assessment Test.
# It handles gender selection, participant info entry, video playback (simulated),
# questions, a break screen, and saving results to Excel.
#
# Note: This version uses placeholder video simulation. In a real deployment,
# you would integrate a proper video player (e.g., flet_video or media controls).

# ----------------------------------------------------------------------------
# CONFIGURATION PATHS AND CONSTANTS
# ----------------------------------------------------------------------------
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
    """
    Main application class for the Flet-based Child Trust Assessment Test.
    
    Manages the entire flow: UI screens, test state, participant data,
    scenario ordering, response collection, and data saving.
    
    Attributes:
        page (ft.Page): The root page object provided by Flet.
        gender (str or None): Selected gender ("girl" or "boy").
        participant (dict or None): Dictionary storing participant details.
        scenario_order (list): Randomized list of 8 scenario names.
        current_index (int): Index of the current scenario (0-7).
        responses (dict): Stores answers per scenario (to be expanded later).
        waiting_for_break (bool): Flag to prevent double break screen after scenario 4.
    """
    
    def __init__(self):
        """Initialize the application with default state variables."""
        self.page = None
        self.gender = None
        self.participant = None
        self.scenario_order = []
        self.current_index = 0
        self.responses = {}
        self.waiting_for_break = False
    
    def run(self, page: ft.Page):
        """
        Entry point called by Flet. Sets up the main window and shows the gender selection screen.
        
        Args:
            page (ft.Page): The root page object provided by the Flet runtime.
        """
        self.page = page
        page.title = "آزمون سنجش اعتماد کودکان"          # Persian: "Child Trust Assessment Test"
        page.theme_mode = ft.ThemeMode.LIGHT           # Light theme for better readability
        page.bgcolor = ft.Colors.WHITE                 # White background
        page.window_width = 1024                       # Window width in pixels
        page.window_height = 768                       # Window height in pixels
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER   # Center horizontally
        page.vertical_alignment = ft.MainAxisAlignment.CENTER       # Center vertically
        
        # Show the first screen: choose boy or girl
        self.show_gender_selection()
        page.update()                                   # Refresh the UI
    
    def show_gender_selection(self):
        """
        Display the gender selection screen with two large buttons (Girls / Boys).
        """
        self.page.clean()                               # Remove all existing controls
        
        # Title text in Persian
        title = ft.Text("آزمون سنجش اعتماد کودکان", size=40, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800)
        
        # Button for girls – pink background
        girl_btn = ft.ElevatedButton(
            content=ft.Text("دختران", size=28, weight=ft.FontWeight.BOLD),
            on_click=lambda e: self.start_test("girl"),   # Call start_test with "girl"
            width=250, height=120,
            style=ft.ButtonStyle(bgcolor=ft.Colors.PINK_400, color=ft.Colors.WHITE)
        )
        
        # Button for boys – blue background
        boy_btn = ft.ElevatedButton(
            content=ft.Text("پسران", size=28, weight=ft.FontWeight.BOLD),
            on_click=lambda e: self.start_test("boy"),    # Call start_test with "boy"
            width=250, height=120,
            style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_400, color=ft.Colors.WHITE)
        )
        
        # Arrange controls vertically with spacing
        self.page.add(
            ft.Column([
                ft.Container(height=100),                # Top spacer
                title,
                ft.Container(height=80),
                ft.Row([girl_btn, boy_btn], alignment=ft.MainAxisAlignment.CENTER, spacing=60),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )
    
    def start_test(self, gender: str):
        """
        Initialize the test for the selected gender.
        
        Steps:
            1. Store the gender.
            2. Randomize the order of the 8 scenarios.
            3. Reset response tracking and break flag.
            4. Show the participant information entry form.
        
        Args:
            gender (str): Either "girl" or "boy".
        """
        self.gender = gender
        self.scenario_order = random.sample(SENARIO_NAMES, 8)   # Random permutation of 8 scenarios
        self.current_index = 0
        self.responses = {}
        self.waiting_for_break = False
        self.show_entry_form()
    
    def show_entry_form(self):
        """
        Display a form to collect participant information: name, age, grade.
        After submission, moves to the video playback screen.
        """
        self.page.clean()
        
        # Text field for full name (RTL alignment for Persian)
        name_field = ft.TextField(label="نام و نام خانوادگی", width=400, text_align=ft.TextAlign.RIGHT)
        
        # Numeric field for age (only numbers allowed)
        age_field = ft.TextField(label="سن", width=200, text_align=ft.TextAlign.RIGHT, input_filter=ft.NumbersOnlyInputFilter())
        
        # Dropdown for school grade (currently only first and second grade)
        grade_field = ft.Dropdown(label="پایه تحصیلی", width=200, options=[
            ft.dropdown.Option("اول"),
            ft.dropdown.Option("دوم")
        ])
        
        def submit(e):
            """Callback for the submit button. Validates inputs and proceeds."""
            if not name_field.value or not age_field.value or not grade_field.value:
                return   # Validation fails – do nothing (could show a snackbar)
            
            # Create participant dictionary with collected info and metadata
            self.participant = {
                "name": name_field.value,
                "age": int(age_field.value),
                "grade": grade_field.value,
                "gender": self.gender,
                "code": random.randint(1000, 9999),           # Random 4-digit participant code
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.show_video()
        
        submit_btn = ft.ElevatedButton("شروع آزمایش", on_click=submit, width=200)
        
        # Layout the form vertically
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
        """
        Display the video playback screen for the current scenario.
        If all 8 scenarios are finished, it calls finish_test().
        If halfway (index == 4) and break not yet shown, it calls show_break().
        
        In this version, video playback is simulated with a placeholder text
        and a "Skip Video" button. In a real implementation, you would embed
        an actual video player (e.g., ft.Video or third-party component).
        """
        # If all scenarios completed, wrap up the test
        if self.current_index >= 8:
            self.finish_test()
            return
        
        # If we reached scenario index 4 (i.e., after completing 4 scenarios) and break not shown yet
        if self.current_index == 4 and not self.waiting_for_break:
            self.waiting_for_break = True
            self.show_break()
            return
        
        self.page.clean()
        
        # Get the current scenario name and build the expected video path
        scenario = self.scenario_order[self.current_index]
        video_path = os.path.join(VIDEO_DIR, self.gender + "s", f"{scenario}.mp4")
        
        # Placeholder: show text indicating video is playing
        video_text = ft.Text(f"در حال پخش ویدئو {scenario}...", size=24)
        
        def next_video(e):
            """
            Callback for the "Skip Video" button. Increments the scenario index
            and displays the next screen (either next video, break, or finish).
            """
            self.current_index += 1
            self.show_video()
        
        next_btn = ft.ElevatedButton("رد کردن ویدئو", on_click=next_video)
        
        # Layout the video placeholder and skip button
        self.page.add(
            ft.Column([
                ft.Container(height=150),
                video_text,
                ft.Container(height=50),
                next_btn,
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )
        
        # Force UI update
        self.page.update()
        
        # Note: In a real application, you would integrate an actual video player here,
        # and the "next" button would appear only after the video finishes or via a callback.
    
    def show_break(self):
        """
        Show a rest break screen with a countdown timer (30 seconds).
        The child can either wait for the timer to expire or click "Skip Break"
        to resume immediately.
        """
        self.page.clean()
        
        # Label to show remaining seconds
        timer_text = ft.Text("زمان باقیمانده: 30", size=30)
        
        def skip(e):
            """Skip the break and proceed to the next video."""
            self.waiting_for_break = False
            self.show_video()
        
        def update_timer(remaining: int):
            """
            Recursive timer update function.
            
            Args:
                remaining (int): Seconds left on the break timer.
            """
            if remaining <= 0:
                # Timer expired: resume test
                self.waiting_for_break = False
                self.show_video()
            else:
                # Update the displayed text and schedule next tick after 1 second
                timer_text.value = f"زمان باقیمانده: {remaining}"
                self.page.update()
                self.page.after(1000, lambda: update_timer(remaining - 1))
        
        skip_btn = ft.ElevatedButton("رد کردن استراحت", on_click=skip)
        
        # Layout the break screen
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
        
        # Start the countdown from 30 seconds
        update_timer(30)
    
    def finish_test(self):
        """
        Finalize the test: save participant data to an Excel file
        and display a completion screen with an exit button.
        
        Note: Currently only saves participant info and not the detailed responses.
        Full response saving should be implemented similarly to the Tkinter version.
        """
        self.page.clean()
        
        # Ensure the data directory exists
        os.makedirs(DATA_DIR, exist_ok=True)
        
        # Build the output filename using the participant's code
        filename = os.path.join(DATA_DIR, f"result_{self.participant['code']}.xlsx")
        
        # Save participant data as a single-row DataFrame
        df = pd.DataFrame([self.participant])
        df.to_excel(filename, index=False)
        
        # Display success message and file path
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
    """
    Entry point for the Flet application.
    Flet will call the `run` method of TrustApp with the page object.
    """
    ft.app(target=TrustApp().run)


if __name__ == "__main__":
    main()