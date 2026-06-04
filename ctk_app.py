# =============================================================================
# IMPORT NECESSARY LIBRARIES
# =============================================================================

import customtkinter as ctk          # Modern GUI toolkit (customizable, themed)
import tkinter as tk                 # Standard Tkinter (used for the video frame)
from tkinter import messagebox       # Dialog boxes for errors/warnings
import random                        # To randomize scenario order
import os                            # File path handling
import pandas as pd                  # Read/write Excel files
from datetime import datetime        # Timestamp for participant data
import vlc                           # Video player backend (libVLC)
import time                          # For potential delays (not heavily used)
from PIL import Image                # Load background image

# =============================================================================
# APPLICATION CONSTANTS (Paths, lists, texts)
# =============================================================================

# File where participant data and scoring keys are stored
SCORING_KEYS_FILE = os.path.join("data", "raw", "scoring_keys.xlsx")
DATA_DIR = os.path.join("data", "raw")                     # Directory for data
VIDEO_DIR = os.path.join("src", "trust_assessment", "assets", "videos")  # Video folder

# Names of the 8 scenarios (SEN1 to SEN8)
SENARIO_NAMES = ["SEN1", "SEN2", "SEN3", "SEN4", "SEN5", "SEN6", "SEN7", "SEN8"]

# Four questions asked after each video, each with a unique key and Persian text
QUESTIONS = [
    {"key": "niceness", "text": "به نظرت این پسر/دختر خوبیه؟"},
    {"key": "trust", "text": "به نظرت تو چقدر از حرفای این پسر/دختر رو قبول می‌کنی؟"},
    {"key": "self_disclosure", "text": "به نظرت تو رازهای خودتو به این پسر/دختر میگی؟"},
    {"key": "correctness", "text": "به نظرت چقدر از جوابای این پسر/دختر درست بود؟"},
]

# Five answer options (Persian) – from "completely disagree" to "completely agree"
ANSWER_OPTIONS = [
    "گزینه 1 ( 😡 هیچکدوم از حرفاشو قبول نمی‌کنم )",
    "گزینه 2 ( 😐 فقط یه کوچولو از حرفاشو قبول می‌کنم )",
    "گزینه 3 ( 😌 نصف حرفاشو قبول می‌کنم )",
    "گزینه 4 ( 😊 بیشتر حرفاشو قبول می‌کنم )",
    "گزینه 5 ( 😍 همه‌ی حرفاشو قبول می‌کنم )",
]

# =============================================================================
# MAIN APPLICATION CLASS
# =============================================================================

class TrustAppWithBackground:
    """
    Main application for a child trust assessment test.
    Shows videos, asks questions, stores answers in Excel.
    Uses a background image (if available) on certain screens.
    """

    def __init__(self):
        """Initialize the main window, load resources, and start gender selection."""
        # Create the main window
        self.root = ctk.CTk()
        self.root.title("آزمون سنجش اعتماد کودکان")   # Window title
        self.root.geometry("1024x768")               # Fixed window size

        # ---- Load background image ----
        # Get the directory where this script is located
        base_path = os.path.dirname(os.path.abspath(__file__))
        bg_path = os.path.join(base_path, "background.png")
        if os.path.exists(bg_path):
            # Create a CTkImage object from the PNG file (size matches window)
            self.bg_image = ctk.CTkImage(light_image=Image.open(bg_path),
                                         dark_image=Image.open(bg_path),
                                         size=(1024, 768))
        else:
            self.bg_image = None
            print("هشدار: فایل background.png پیدا نشد. از رنگ پیش‌فرض استفاده می‌شود.")

        # Widget that will hold the background image (created later)
        self.bg_label = None
        # Place the background initially (with image if available)
        self.set_background(use_image=True)

        # ---- Define custom fonts (Persian-friendly) ----
        self.font_title = ctk.CTkFont(family="Yekan Bakh", size=32, weight="bold")
        self.font_subtitle = ctk.CTkFont(family="Yekan Bakh", size=24, weight="bold")
        self.font_button = ctk.CTkFont(family="Yekan Bakh", size=18, weight="bold")
        self.font_question = ctk.CTkFont(family="Sahel", size=32, weight="bold")
        self.font_option_text = ctk.CTkFont(family="Sahel", size=22)
        self.font_label = ctk.CTkFont(family="Sahel", size=14)

        # ---- State variables ----
        self.gender = None            # "girl" or "boy"
        self.participant = None       # Dict with name, age, grade, gender, date
        self.scenario_order = []      # Randomized list of 8 scenario names
        self.current_index = 0        # Which scenario we are at (0..7)
        self.responses = {}           # Final answers: {scenario: {question_key: answer_value}}
        self.break_completed = False  # Whether the mid‑test break has been shown
        self.break_timer_id = None    # ID for the after() timer of the break

        # VLC video player related
        self.vlc_instance = None
        self.vlc_player = None
        self.video_frame = None       # Tkinter frame that hosts the video
        self.is_playing = False       # Playback state

        # Question navigation
        self.current_question_index = 0   # 0..3 for the four questions
        self.current_scenario = None      # Scenario currently being answered
        self.temp_answers = {}            # Answers for the current scenario (before saving)

        # Gold standard options (correct answers from Excel sheet Sheet2)
        self.gold_standard_options = {}

        # Load gold standards from the Excel file (if exists)
        self.load_gold_standards()

        # Start with the gender selection screen
        self.show_gender_selection()

    # -------------------------------------------------------------------------
    # BACKGROUND MANAGEMENT
    # -------------------------------------------------------------------------

    def set_background(self, use_image=True):
        """
        Show or hide the background image.
        If use_image == True and a background image exists, create a label with it.
        Otherwise, destroy the background label and set a default window color.
        """
        if self.bg_label:
            self.bg_label.destroy()       # Remove old background label

        if use_image and self.bg_image:
            # Create a label that fills the whole window with the image
            self.bg_label = ctk.CTkLabel(self.root, image=self.bg_image, text="")
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            self.bg_label.lower()         # Send it to the back so other widgets appear on top
        else:
            self.bg_label = None
            # Fallback to a light blue background
            self.root.configure(fg_color="#E3F2FD")

    def clear_window(self):
        """
        Remove all widgets except the background image.
        Also cancel any break timer and stop VLC player if running.
        """
        if self.break_timer_id:
            self.root.after_cancel(self.break_timer_id)   # Cancel pending timer
            self.break_timer_id = None

        if self.vlc_player:
            self.vlc_player.stop()        # Stop video playback
            self.vlc_player = None

        # Iterate over all children of the root window, keep only the background label
        for widget in self.root.winfo_children():
            if widget != self.bg_label:
                widget.destroy()

    # -------------------------------------------------------------------------
    # GOLD STANDARD (CORRECT ANSWERS) LOADING
    # -------------------------------------------------------------------------

    def load_gold_standards(self):
        """
        Read the scoring_keys.xlsx, sheet 'Sheet2'.
        Look for rows where 'شماره گزینه' contains an asterisk (*)
        and store the numeric value (without *) under the scenario name.
        """
        if not os.path.exists(SCORING_KEYS_FILE):
            return   # No file, nothing to load

        try:
            df = pd.read_excel(SCORING_KEYS_FILE, sheet_name='Sheet2')
            df = df.dropna(subset=['سناریو', 'شماره گزینه'])   # Remove missing rows
            for _, row in df.iterrows():
                scenario = str(row["سناریو"]).strip()
                opt_val = str(row["شماره گزینه"]).strip()
                if '*' in opt_val:
                    num = int(opt_val.replace('*', '').strip())
                    self.gold_standard_options[scenario] = num
        except Exception as e:
            print(f"خطا در بارگذاری گزینه‌های طلایی: {e}")

    def get_gold_standard(self, scenario):
        """Return the gold standard option number for the given scenario, or None."""
        return self.gold_standard_options.get(scenario, None)

    # -------------------------------------------------------------------------
    # GENDER SELECTION SCREEN
    # -------------------------------------------------------------------------

    def show_gender_selection(self):
        """
        Display two buttons (Girls / Boys) on a background image.
        The user's choice determines the gender for the rest of the test.
        """
        self.clear_window()
        self.set_background(use_image=True)   # Ensure background is visible

        # Transparent frame to hold UI elements (so the background shows through)
        frame = ctk.CTkFrame(self.root, fg_color="transparent")
        frame.pack(expand=True, fill="both", padx=40, pady=40)

        title = ctk.CTkLabel(frame, text="آزمون سنجش اعتماد کودکان", font=self.font_title)
        title.pack(pady=50)

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(pady=50)

        # Button for girls (pink)
        girl_btn = ctk.CTkButton(btn_frame, text="دختران", font=self.font_button,
                                  width=200, height=80, corner_radius=20, fg_color="#FF69B4",
                                  command=lambda: self.start_test("girl"))
        girl_btn.pack(side="left", padx=30)

        # Button for boys (blue)
        boy_btn = ctk.CTkButton(btn_frame, text="پسران", font=self.font_button,
                                width=200, height=80, corner_radius=20, fg_color="#4169E1",
                                command=lambda: self.start_test("boy"))
        boy_btn.pack(side="left", padx=30)

    # -------------------------------------------------------------------------
    # START TEST: RANDOMIZE SCENARIO ORDER AND GO TO ENTRY FORM
    # -------------------------------------------------------------------------

    def start_test(self, gender):
        """
        Called after gender selection.
        Stores gender, randomizes the order of the 8 scenarios,
        and shows the participant information form.
        """
        self.gender = gender
        # Randomly shuffle the list of scenario names (in‑place shuffle via random.sample)
        self.scenario_order = random.sample(SENARIO_NAMES, 8)
        self.current_index = 0
        self.responses = {}
        self.break_completed = False
        self.show_entry_form()   # Move to the form

    # -------------------------------------------------------------------------
    # PARTICIPANT INFORMATION FORM
    # -------------------------------------------------------------------------

    def show_entry_form(self):
        """
        Ask for the child's name, age, and grade.
        The background image is still present (we did not remove it).
        """
        self.clear_window()
        # Background remains because we never called set_background(False) here

        frame = ctk.CTkFrame(self.root, fg_color="transparent")
        frame.pack(expand=True, fill="both", padx=40, pady=40)

        title = ctk.CTkLabel(frame, text="اطلاعات کودک", font=self.font_subtitle)
        title.pack(pady=30)

        # Name entry
        name_entry = ctk.CTkEntry(frame, placeholder_text="نام و نام خانوادگی", width=400, font=self.font_label)
        name_entry.pack(pady=10)

        # Age entry (expects integer)
        age_entry = ctk.CTkEntry(frame, placeholder_text="سن", width=200, font=self.font_label)
        age_entry.pack(pady=10)

        # Grade dropdown (grades 1 to 6)
        grades = ["اول", "دوم", "سوم", "چهارم", "پنجم", "ششم"]
        grade_combo = ctk.CTkComboBox(frame, values=grades, font=self.font_label, width=200)
        grade_combo.pack(pady=10)
        grade_combo.set("اول")   # Default selection

        def submit():
            """Validate inputs, store participant info, and move to video playback."""
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
            self.show_video()   # Start showing the first video

        submit_btn = ctk.CTkButton(frame, text="شروع آزمایش", font=self.font_button,
                                    width=200, height=50, corner_radius=15, command=submit)
        submit_btn.pack(pady=30)

    # -------------------------------------------------------------------------
    # VIDEO PLAYBACK SCREEN
    # -------------------------------------------------------------------------

    def show_video(self):
        """
        Display a VLC video player inside a tk.Frame.
        The background image is removed (set_background(False)).
        If all 8 videos have been shown, save data and finish.
        """
        self.set_background(use_image=False)   # Remove background for video screens
        if self.current_index >= 8:
            self.save_to_excel()
            self.finish_test()
            return

        self.clear_window()   # Clear any previous widgets

        frame = ctk.CTkFrame(self.root, fg_color="transparent")
        frame.pack(expand=True, fill="both", padx=40, pady=40)

        scenario = self.scenario_order[self.current_index]
        title = ctk.CTkLabel(frame, text=f"ویدئو {scenario} - ویدئو شماره {self.current_index + 1} از 8", font=self.font_subtitle)
        title.pack(pady=20)

        # Create a tk.Frame (not CTk) because VLC requires a native window handle
        self.video_frame = tk.Frame(frame, bg="black", width=900, height=600)
        self.video_frame.pack(pady=10)
        self.video_frame.pack_propagate(False)   # Keep fixed size

        # Control buttons frame
        control_frame = ctk.CTkFrame(frame, fg_color="transparent")
        control_frame.pack(pady=10)

        # Pause/Play button
        self.pause_play_btn = ctk.CTkButton(control_frame, text="⏸️ توقف", font=self.font_button,
                                            width=100, height=40, corner_radius=15, fg_color="#555555",
                                            command=self.toggle_pause)
        self.pause_play_btn.pack(side="left", padx=10)

        # Rewind 15 seconds button
        rewind_btn = ctk.CTkButton(control_frame, text="⏪ 15 ثانیه", font=self.font_button,
                                   width=120, height=40, corner_radius=15, fg_color="#FF9800",
                                   command=self.rewind_15)
        rewind_btn.pack(side="left", padx=10)

        # Skip video button (immediately ends playback and goes to questions)
        skip_btn = ctk.CTkButton(control_frame, text="رد کردن ویدئو", font=self.font_button,
                                 width=120, height=40, corner_radius=15, fg_color="#F44336",
                                 command=self.skip_video)
        skip_btn.pack(side="left", padx=10)

        # Construct video file path based on gender and scenario
        # e.g., videos/girls/SEN1.mp4  or  videos/boys/SEN1.mp4
        video_path = os.path.join(VIDEO_DIR, self.gender + "s", f"{scenario}.mp4")
        if os.path.exists(video_path):
            # Initialize VLC instance and player
            self.vlc_instance = vlc.Instance()
            self.vlc_player = self.vlc_instance.media_player_new()
            media = self.vlc_instance.media_new(video_path)
            self.vlc_player.set_media(media)
            # Embed video into the tk.Frame using its window handle (winfo_id)
            self.vlc_player.set_hwnd(self.video_frame.winfo_id())
            self.vlc_player.play()
            self.is_playing = True
            # Start polling for video end
            self.check_video_end()
        else:
            messagebox.showerror("خطا", f"ویدئوی {scenario} یافت نشد")
            # If video missing, skip to questions anyway
            self.show_questions()

    def toggle_pause(self):
        """Pause or resume video playback."""
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
        """Jump 15 seconds back in the video. If paused, start playing again."""
        if not self.vlc_player:
            return
        current_time = self.vlc_player.get_time()
        new_time = max(0, current_time - 15000)   # cannot go below 0
        self.vlc_player.set_time(new_time)
        if not self.is_playing:
            # automatically resume after rewinding
            self.vlc_player.play()
            self.is_playing = True
            self.pause_play_btn.configure(text="⏸️ توقف")

    def check_video_end(self):
        """
        Periodically check VLC state. If state is Ended, call video_finished().
        Otherwise, schedule another check after 500 ms.
        """
        if self.vlc_player:
            state = self.vlc_player.get_state()
            if state == vlc.State.Ended:
                self.video_finished()
            else:
                self.root.after(500, self.check_video_end)

    def video_finished(self):
        """Stop playback and proceed to questions."""
        if self.vlc_player:
            self.vlc_player.stop()
            self.vlc_player = None
        self.is_playing = False
        self.show_questions()

    def skip_video(self):
        """Skip the current video (stop player) and go to questions."""
        if self.vlc_player:
            self.vlc_player.stop()
            self.vlc_player = None
        self.is_playing = False
        self.show_questions()

    # -------------------------------------------------------------------------
    # QUESTIONNAIRE SCREENS
    # -------------------------------------------------------------------------

    def show_questions(self):
        """
        Decide whether to show the 4‑question set for the current scenario,
        a break screen (after scenario 4), or end the test.
        Also removes background image.
        """
        self.set_background(use_image=False)   # Ensure no background on question screens
        if self.current_index >= 8:
            self.save_to_excel()
            self.finish_test()
            return

        # After the 4th video (index 4, because 0‑based) we show a break screen.
        # But only if break has not been shown already.
        if self.current_index == 4 and not self.break_completed:
            self.break_completed = True
            self.show_break()
            return

        # Initialize question process for the current scenario
        self.current_scenario = self.scenario_order[self.current_index]
        self.current_question_index = 0
        self.temp_answers = {}   # answers will be stored here temporarily
        self.display_question()

    def display_question(self):
        """
        Show one question at a time.
        When all 4 questions are answered, save the answers for this scenario
        and move to the next video.
        """
        
        if self.current_question_index >= len(QUESTIONS):
            # All 4 questions answered -> store temp_answers in final responses
            self.responses[self.current_scenario] = self.temp_answers
            self.current_index += 1    # go to next scenario
            self.show_video()          # play next video (or finish)
            return

        self.clear_window()   # Remove previous widgets

        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=40, pady=40)

        q_number = self.current_question_index + 1
        q_data = QUESTIONS[self.current_question_index]

        # Header showing scenario name and question number
        header = ctk.CTkLabel(main_frame, text=f"{self.current_scenario} - سوال {q_number} از 4", 
                              font=self.font_subtitle)
        header.pack(pady=20)

        # The question text
        question_text = ctk.CTkLabel(main_frame, text=q_data["text"], font=self.font_question,
                                     justify="right", anchor="e", wraplength=900)
        question_text.pack(pady=40, padx=30, anchor="e")

        # Gold standard value is used only for scoring, not displayed as star
        gold_opt = self.get_gold_standard(self.current_scenario)   # kept for possible future use
        answer_var = tk.IntVar(value=0)   # 0 means no selection yet

        # Scrollable frame for the 5 answer options
        options_frame = ctk.CTkScrollableFrame(main_frame, fg_color="white", border_width=2, border_color="#CCCCCC")
        options_frame.pack(fill="both", expand=True, padx=20, pady=20)

        for i, opt_text in enumerate(ANSWER_OPTIONS, 1):
            opt_container = ctk.CTkFrame(options_frame, fg_color="transparent")
            opt_container.pack(fill="x", pady=8, padx=10)

            # Radio button – color depends on gender (pink for girls, blue for boys)
            radio = ctk.CTkRadioButton(opt_container, variable=answer_var, value=i, text="",
                                       fg_color=("#3B8ED0", "#1F6AA5") if self.gender == "boy" else ("#E91E63", "#C2185B"),
                                       hover_color=("#3B8ED0", "#1F6AA5") if self.gender == "boy" else ("#E91E63", "#C2185B"),
                                       border_color="#666666")
            radio.pack(side="right", padx=(10, 5))

            # Display the answer text (no star anymore, as requested by user)
            display_text = opt_text

            # Label that shows the text; clicking on it also selects the radio button
            label = ctk.CTkLabel(opt_container, text=display_text, font=self.font_option_text,
                                 anchor="e", justify="right", wraplength=700, text_color="#000000")
            label.pack(side="right", fill="x", expand=True, padx=(5, 10))
            # Bind mouse click to set the variable and select the radio
            label.bind("<Button-1>", lambda e, rb=radio, var=answer_var, val=i: (var.set(val), rb.select()))
            opt_container.bind("<Button-1>", lambda e, rb=radio, var=answer_var, val=i: (var.set(val), rb.select()))

        def next_question():
            """Save the selected answer and move to the next question."""
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

    # -------------------------------------------------------------------------
    # BREAK SCREEN (after scenario 4)
    # -------------------------------------------------------------------------

    def show_break(self):
        """
        Show a 30‑second break screen with a countdown timer.
        User can skip the break early.
        Background image is removed (clean interface for break).
        """
        self.set_background(use_image=False)
        self.clear_window()

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
                self.show_video()          # break finished, continue test
            else:
                remaining -= 1
                timer_label.configure(text=f"زمان باقیمانده: {remaining} ثانیه")
                self.break_timer_id = self.root.after(1000, update_timer)

        def skip():
            """Cancel the timer and immediately continue."""
            if self.break_timer_id:
                self.root.after_cancel(self.break_timer_id)
                self.break_timer_id = None
            self.show_video()

        skip_btn = ctk.CTkButton(frame, text="رد کردن استراحت", font=self.font_button,
                                 width=200, height=40, corner_radius=15, fg_color="#FF9800", command=skip)
        skip_btn.pack(pady=20)

        update_timer()   # start the countdown

    # -------------------------------------------------------------------------
    # EXCEL SAVING (RESPONSES & SCORES)
    # -------------------------------------------------------------------------

    def get_next_row_number(self):
        """
        Read the existing Sheet1 of scoring_keys.xlsx,
        find the maximum 'ردیف' (row number) and return row_number + 1.
        If file does not exist or sheet is empty, return 1.
        """
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
        """
        Look up the scoring keys (Sheet2) for a given scenario and chosen answer.
        Returns a dict with 'mistrust', 'trust', 'gullibility' scores.
        If not found, returns zeros.
        """
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
        """
        Save participant data, raw answers, and computed scores to scoring_keys.xlsx.
        Three sheets:
          Sheet1 – participant info + raw answers for each scenario.
          Sheet2 – scoring keys (read‑only, already exists).
          Sheet3 – calculated mistrust, trust, gullibility totals per question type.
        """
        os.makedirs(DATA_DIR, exist_ok=True)

        # Ensure we have exactly 8 scenarios answered
        if len(self.responses) != 8:
            messagebox.showerror("خطا", f"تعداد پاسخ‌ها {len(self.responses)} است، باید 8 باشد. ذخیره نشد.")
            return

        row_number = self.get_next_row_number()

        # Load existing sheets if the file already exists
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

        # ---- Build row for Sheet1 (raw answers) ----
        row1 = {"ردیف": row_number, "نام": self.participant["name"], "سن": self.participant["age"], "کلاس": self.participant["grade"]}
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

        # ---- Compute totals for Sheet3 ----
        order_str = ''.join([s.replace('SEN', '') for s in self.scenario_order])   # e.g. "37521846"
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

        # Build row for Sheet3 (aggregated scores)
        row3 = {
            "ردیف": row_number, "نام": self.participant["name"], "سن": self.participant["age"], "کلاس": self.participant["grade"],
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

        # Load Sheet2 (scoring keys) unchanged
        try:
            if os.path.exists(SCORING_KEYS_FILE):
                scoring_keys_df = pd.read_excel(SCORING_KEYS_FILE, sheet_name='Sheet2')
            else:
                scoring_keys_df = pd.DataFrame()
        except:
            scoring_keys_df = pd.DataFrame()

        # Write all three sheets to the Excel file (overwrite)
        try:
            with pd.ExcelWriter(SCORING_KEYS_FILE, engine='openpyxl', mode='w') as writer:
                sheet1_df.to_excel(writer, sheet_name='Sheet1', index=False)
                scoring_keys_df.to_excel(writer, sheet_name='Sheet2', index=False)
                sheet3_df.to_excel(writer, sheet_name='Sheet3', index=False)
            print("فایل با موفقیت ذخیره شد.")
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در ذخیره فایل Excel: {str(e)}")

    # -------------------------------------------------------------------------
    # FINISH & RESTART
    # -------------------------------------------------------------------------

    def finish_test(self):
        """
        Display a completion screen with thank you message and options to quit or restart.
        Background image is shown again.
        """
        self.clear_window()
        self.set_background(use_image=True)   # Show the background again

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
        """
        Reset all state variables and return to the gender selection screen.
        Stops any playing video and cancels break timer if active.
        """
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

    # -------------------------------------------------------------------------
    # MAIN LOOP
    # -------------------------------------------------------------------------

    def run(self):
        """Start the Tkinter event loop."""
        self.root.mainloop()


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    app = TrustAppWithBackground()
    app.run()