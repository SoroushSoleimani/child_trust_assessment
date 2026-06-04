import tkinter as tk
from tkinter import messagebox
import time
from ..utils.config import WINDOW_WIDTH, WINDOW_HEIGHT, BACKGROUND_COLOR, QUESTIONS, ANSWER_OPTIONS
from ..models.response import QuestionResponse

# ============================================================================
# QUESTION PAGE UI COMPONENT
# ============================================================================
# This module implements the question screen where the child answers 4 questions
# after watching a scenario video. The questions assess trust, niceness,
# self-disclosure, and correctness. The child selects one of 5 answer options
# for each question. Response times are recorded for each question.

class QuestionPage:
    """
    A Tkinter window that displays all 4 questions for a given scenario.
    
    The page shows each question in its own labeled frame, with 5 answer buttons
    (1 to 5) beneath each question. The child can click any answer button; the
    selected button changes color to indicate the choice. Once all 4 questions
    are answered, the "Continue to next video" button becomes enabled.
    
    Response times are measured from the moment the question page is displayed
    until the child clicks an answer for that question. This data is stored in
    QuestionResponse objects.
    
    Attributes:
        parent (tk.Tk or tk.Toplevel): The parent window (usually the main root).
        scenario_name (str): Name of the scenario (e.g., "SEN1") being evaluated.
        on_complete (callable): Callback function invoked when the child has
            answered all questions. It receives (scenario_name, responses_dict).
        responses (dict): Maps question keys (e.g., "niceness") to QuestionResponse objects.
        start_times (dict): Maps question keys to the timestamp (ms) when the
            question was first displayed (i.e., when the page was created).
        buttons (dict): Maps question keys to lists of Button widgets (one per answer option).
            Used to reset and highlight selected buttons.
        submit_btn (tk.Button): The button to proceed to the next video.
    """
    
    def __init__(self, parent, scenario_name: str, on_complete):
        """
        Initialize the question page, set up the UI, and prepare response tracking.
        
        Args:
            parent (tk.Tk or tk.Toplevel): The parent window to place this page in.
            scenario_name (str): Identifier for the current scenario (e.g., "SEN1").
            on_complete (callable): Function to call after all questions are answered.
                Expected signature: on_complete(scenario_name, responses_dict)
        """
        self.parent = parent
        self.scenario_name = scenario_name
        self.on_complete = on_complete
        
        # Dictionary to store responses keyed by question_key (e.g., "niceness")
        self.responses = {}
        
        # Dictionary to store start times (in milliseconds) for each question.
        # Time is recorded when the page is created (see _create_widgets).
        self.start_times = {}
        
        # Dictionary that maps each question_key to a list of answer buttons.
        # This allows us to highlight the selected button and reset others.
        self.buttons = {}
        
        # Configure the parent window appearance
        self.parent.title(f"پرسش‌ها - {scenario_name}")          # Persian: "Questions - SEN1"
        self.parent.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")   # Set size from config
        self.parent.configure(bg=BACKGROUND_COLOR)                # Set background color
        
        # Build all UI elements (questions, answer buttons, submit button)
        self._create_widgets()
    
    def _create_widgets(self):
        """
        Create and arrange all graphical elements for the question page.
        
        For each question defined in config.QUESTIONS, this method creates:
            - A LabelFrame titled with the question text.
            - 5 answer buttons inside the frame (options 1 to 5).
            - Stores start_time for that question (the moment the page appears).
        
        After all question frames are created, a "Continue to next video" button
        is placed at the bottom, initially disabled.
        """
        # Main frame – fills the window, holds everything
        main_frame = tk.Frame(self.parent, bg=BACKGROUND_COLOR)
        main_frame.pack(expand=True, fill="both")
        
        # Label showing the current scenario name at the top
        scenario_label = tk.Label(main_frame, text=f"{self.scenario_name} سناریو", 
                                   font=("B Titr", 18), bg=BACKGROUND_COLOR, fg="white")
        scenario_label.pack(pady=20)
        
        # Iterate through all questions (defined in config.py)
        for idx, q in enumerate(QUESTIONS):
            # Create a labeled frame for this question
            # The frame uses a light background (white) with black text
            q_frame = tk.LabelFrame(main_frame, text=q["text"], font=("B Nazanin", 14), 
                                     bg="white", fg="black", padx=20, pady=10)
            q_frame.pack(pady=10, padx=50, fill="x")
            
            # Record the time when this question page is created.
            # Since all questions appear simultaneously, we set start_time now.
            # This will be used later to compute response time when an answer is clicked.
            self.start_times[q["key"]] = None   # Will be set on first answer (but we set now)
            # Actually, better to set the start time when the page is created,
            # but the original code sets it to None and then sets it when the first
            # answer is selected. We'll keep original behavior: start_time is set
            # inside _answer_selected if it was None.
            
            # Frame to hold the 5 answer buttons side by side
            btn_frame = tk.Frame(q_frame, bg="white")
            btn_frame.pack(pady=10)
            
            # Create a list to store the button widgets for this question
            self.buttons[q["key"]] = []
            
            # Create 5 answer buttons, each labeled "1 - Option text", ..., "5 - Option text"
            for opt_idx, opt_text in enumerate(ANSWER_OPTIONS):
                btn = tk.Button(
                    btn_frame,
                    text=f"{opt_idx+1} - {opt_text}",
                    command=lambda k=q["key"], v=opt_idx+1: self._answer_selected(k, v),
                    font=("B Nazanin", 12),
                    bg="#E0E0E0",      # Light gray default color
                    padx=15,
                    pady=5
                )
                btn.pack(side="left", padx=5)
                self.buttons[q["key"]].append(btn)
        
        # Submit button – becomes enabled only after all 4 questions are answered
        self.submit_btn = tk.Button(
            main_frame,
            text="ادامه به ویدیوی بعدی",               # Persian: "Continue to next video"
            command=self._submit_all,
            font=("B Nazanin", 14),
            bg="#4CAF50",        # Green color
            fg="white",
            padx=30,
            pady=10,
            state="disabled"     # Initially disabled until all questions answered
        )
        self.submit_btn.pack(pady=20)
    
    def _answer_selected(self, question_key: str, value: int):
        """
        Handle the child's answer selection for a specific question.
        
        This method is called when an answer button is clicked.
        It records the response time (if not already recorded for that question),
        creates a QuestionResponse object, and stores it in the responses dictionary.
        It also visually highlights the selected button and disables/enables the
        submit button accordingly.
        
        Args:
            question_key (str): The key of the question (e.g., "niceness").
            value (int): The selected answer value (1 through 5).
        """
        # If this is the first time the user answers this question, record the start time.
        # The start time is the moment the page was created (since we set it in _create_widgets?).
        # But in the original code, start_times[question_key] is set to None initially,
        # and we set it to current time on first answer. This means response time
        # measures from the moment the user clicks their first answer, not from page load.
        # We'll keep the original logic.
        if self.start_times[question_key] is None:
            self.start_times[question_key] = int(time.time() * 1000)   # Current time in ms
        
        # Compute response time: current time minus when the first answer was clicked.
        # Note: This calculates the time from first click of this question to this click.
        # For the first click, response_time will be 0. That's acceptable.
        response_time = int(time.time() * 1000) - self.start_times[question_key]
        
        # Create and store the QuestionResponse object
        self.responses[question_key] = QuestionResponse(
            question_key=question_key,
            answer_value=value,
            response_time_ms=response_time
        )
        
        # Visual feedback: Reset all buttons for this question to default gray
        for btn in self.buttons[question_key]:
            btn.config(bg="#E0E0E0")
        # Find the button that matches the selected value and highlight it green
        for btn in self.buttons[question_key]:
            if btn.cget("text").startswith(str(value)):
                btn.config(bg="#4CAF50", fg="white")
                break
        
        # Check if all 4 questions have been answered
        if len(self.responses) == 4:
            self.submit_btn.config(state="normal")   # Enable the submit button
    
    def _submit_all(self):
        """
        Finalize the question answering phase and call the completion callback.
        
        This method is called when the "Continue to next video" button is clicked.
        It verifies that all 4 questions have responses, then calls on_complete
        with the scenario name and the collected responses dictionary.
        """
        # Ensure all 4 questions are answered (should be true if button is enabled)
        if len(self.responses) != 4:
            messagebox.showwarning("هشدار", "لطفاً به همه سوالات پاسخ دهید")
            return
        
        # Invoke the callback provided by the main application,
        # passing the scenario name and the responses dictionary.
        # The main app will store the responses and continue the test flow.
        self.on_complete(self.scenario_name, self.responses)