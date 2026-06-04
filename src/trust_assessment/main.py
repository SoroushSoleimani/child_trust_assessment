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
    """
    Main application class for the Child Trust Assessment Test.
    Manages the overall flow: gender selection, participant info entry,
    video playback, questions, break screen, and final data saving.
    """
    
    def __init__(self):
        """Initialize the main Tkinter window and application state variables."""
        self.root = tk.Tk()                     # Create the root window
        self.root.title("آزمون سنجش اعتماد کودکان")  # Window title in Persian
        self.excel_service = ExcelService()     # Service for saving data to Excel
        self.session = None                     # Will hold the current test session
        self.video_service = None               # Service to manage video paths
        self.current_scenario_index = 0         # Index of current scenario (0-7)
        self.scenario_order = []                # Randomized order of scenario names
        self.waiting_for_break = False          # Flag to avoid double break screen
    
    def run(self):
        """Start the application by showing gender selection screen."""
        self.show_gender_selection()
        self.root.mainloop()                    # Start the Tkinter event loop
    
    def show_gender_selection(self):
        """
        Display the initial screen where the child chooses their gender.
        Clears any existing widgets and sets up two large buttons (girl/boy).
        """
        # Remove all existing widgets from the root window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.root.geometry("1024x768")          # Set window size
        
        # Main frame with a green background color
        main_frame = tk.Frame(self.root, bg="#2E7D64")
        main_frame.pack(expand=True)
        
        # Title label
        title = tk.Label(main_frame, text="آزمون سنجش اعتماد کودکان", 
                         font=("B Titr", 28), bg="#2E7D64", fg="white")
        title.pack(pady=50)
        
        # Frame to hold the two gender buttons side by side
        btn_frame = tk.Frame(main_frame, bg="#2E7D64")
        btn_frame.pack(pady=40)
        
        # Button for girls – pink color, calls start_test("girl")
        girl_btn = tk.Button(btn_frame, text="دختران", command=lambda: self.start_test("girl"),
                             font=("B Nazanin", 20), bg="#FF69B4", fg="white", padx=40, pady=20)
        girl_btn.pack(side="left", padx=30)
        
        # Button for boys – blue color, calls start_test("boy")
        boy_btn = tk.Button(btn_frame, text="پسران", command=lambda: self.start_test("boy"),
                            font=("B Nazanin", 20), bg="#4169E1", fg="white", padx=40, pady=20)
        boy_btn.pack(side="left", padx=30)
    
    def start_test(self, gender: str):
        """
        Called after gender selection. Initializes video service with chosen gender,
        checks that all required video files exist, randomizes scenario order,
        and opens the participant information entry window.
        
        Args:
            gender (str): Either "girl" or "boy"
        """
        # Create video service for the chosen gender (handles path resolution)
        self.video_service = VideoService(gender)
        
        # Verify that all scenario videos exist in the corresponding folder
        if not self.video_service.check_videos_exist():
            messagebox.showerror("خطا", "فایل‌های ویدیویی کامل نیستند.\nلطفاً ویدیوهای مورد نیاز را در پوشه مربوطه قرار دهید.")
            return
        
        # Get a randomized order of the 8 scenario names (e.g., SEN1, SEN2, ...)
        self.scenario_order = self.video_service.get_random_order()
        
        # Clear the root window to prepare for the entry form
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Open the participant information entry window.
        # Pass the callback `on_participant_submit` that will be called when the form is submitted.
        entry = EntryWindow(self.root, self.on_participant_submit, gender_selection=False)
    
    def on_participant_submit(self, participant: Participant):
        """
        Callback method invoked when the participant information form is submitted.
        Stores the participant's gender, assigns a random 4-digit code,
        creates a TestSession object, and starts the first video.
        
        Args:
            participant (Participant): Object containing name, age, grade, etc.
        """
        # Set the participant's gender based on the video service's gender
        participant.gender = "girl" if self.video_service.gender == "girl" else "boy"
        participant.code = random.randint(1000, 9999)   # Generate a random participant code
        
        # Create a new test session with the participant and the randomized scenario order
        self.session = TestSession(
            participant=participant,
            scenario_order=self.scenario_order,
            current_scenario_index=0
        )
        
        # Reset state variables for a fresh test
        self.current_scenario_index = 0
        self.waiting_for_break = False
        
        # Show the first video (scenario 0)
        self.show_video()
    
    def show_video(self):
        """
        Display the video player for the current scenario.
        If all 8 scenarios have been completed, it calls finish_test().
        Otherwise, it retrieves the correct video path and starts playback.
        """
        # If we've finished all scenarios, wrap up the test
        if self.current_scenario_index >= 8:
            self.finish_test()
            return
        
        # Clear any existing widgets from the root window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.root.geometry("1024x768")      # Ensure window size
        
        # Get the scenario name for the current index (e.g., "SEN1")
        scenario_name = self.scenario_order[self.current_scenario_index]
        
        # Get the full file path to the corresponding MP4 video
        video_path = self.video_service.get_video_path(scenario_name)
        
        if not video_path:
            messagebox.showerror("خطا", f"ویدیوی {scenario_name} یافت نشد")
            return
        
        # Create a VideoPlayer widget, passing the root window, video path, and a callback
        # that will be called when the video finishes playing.
        player = VideoPlayer(self.root, video_path, self.on_video_complete)
        player.play()       # Start playing the video
    
    def on_video_complete(self):
        """
        Callback method executed when a video finishes playing.
        It triggers the display of the question page for the current scenario.
        """
        scenario_name = self.scenario_order[self.current_scenario_index]
        self.show_questions(scenario_name)
    
    def show_questions(self, scenario_name: str):
        """
        Open the question page for the given scenario.
        Clears the window and creates a QuestionPage widget.
        
        Args:
            scenario_name (str): Name of the scenario (e.g., "SEN1")
        """
        # Remove all existing widgets to prepare for the question page
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create the question page; it will call on_questions_complete when done
        question_page = QuestionPage(self.root, scenario_name, self.on_questions_complete)
    
    def on_questions_complete(self, scenario_name: str, responses: dict):
        """
        Callback method called after the child answers all 4 questions for a scenario.
        Stores the responses in the session, then either shows a break (after scenario 4)
        or proceeds to the next video (or finishes the test if all scenarios done).
        
        Args:
            scenario_name (str): Name of the scenario just answered
            responses (dict): Dictionary mapping question keys (niceness, trust, etc.) to answer values (1-5)
        """
        # Add each response to the session using the session's method
        for q_key, response in responses.items():
            self.session.add_response(scenario_name, response)
        
        # Move to the next scenario index
        self.current_scenario_index += 1
        
        # Check if we have just completed the 4th scenario (index 4 means scenarios 0-3 done)
        # and the break hasn't been shown yet.
        if self.current_scenario_index == 4 and not self.waiting_for_break:
            self.waiting_for_break = True
            self.show_break()                # Show the rest break screen
        elif self.current_scenario_index >= 8:
            self.finish_test()               # All 8 scenarios done
        else:
            self.waiting_for_break = False
            self.show_video()                # Play the next video
    
    def show_break(self):
        """
        Display a break screen (top-level window) that gives the child a short rest.
        The break window contains a timer and a skip button.
        When the break is complete, it resumes the test by showing the next video.
        """
        # Create a new top-level window for the break
        break_window = tk.Toplevel(self.root)
        break_window.title("استراحت")
        break_window.geometry("1024x768")
        
        # Define the callback that will be called when the break finishes
        def on_break_complete():
            break_window.destroy()           # Close the break window
            self.waiting_for_break = False
            self.show_video()                # Continue with the next video
        
        # Instantiate the BreakWindow UI (it handles countdown and button)
        BreakWindow(break_window, on_break_complete)
    
    def finish_test(self):
        """
        Finalize the test: save all collected data to an Excel file using ExcelService,
        then display a completion screen with options to exit or start a new test.
        """
        # Safety check: if no session exists, do nothing
        if self.session is None:
            return
        
        # Save the session data to Excel; the service returns the filename saved
        try:
            filename = self.excel_service.save_session(self.session)
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در ذخیره اطلاعات: {str(e)}")
            return
        
        # Clear all widgets from the root window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create a completion screen
        finish_frame = tk.Frame(self.root, bg="#2E7D64")
        finish_frame.pack(expand=True)
        
        thanks = tk.Label(finish_frame, text="آزمایش با موفقیت انجام شد", 
                          font=("B Titr", 24), bg="#2E7D64", fg="white")
        thanks.pack(pady=50)
        
        info = tk.Label(finish_frame, text=f"داده‌های شما در فایل زیر ذخیره شد:\n{filename}", 
                        font=("B Nazanin", 14), bg="#2E7D64", fg="#FFD700")
        info.pack(pady=30)
        
        # Button frame for two action buttons
        btn_frame = tk.Frame(finish_frame, bg="#2E7D64")
        btn_frame.pack(pady=20)
        
        # Exit button – quits the entire application
        close_btn = tk.Button(btn_frame, text="خروج", command=self.root.quit,
                              font=("B Nazanin", 14), bg="#F44336", fg="white", padx=30, pady=10)
        close_btn.pack(side="left", padx=20)
        
        # New test button – resets all state and returns to gender selection
        new_btn = tk.Button(btn_frame, text="آزمون جدید", command=self.reset_and_restart,
                            font=("B Nazanin", 14), bg="#2196F3", fg="white", padx=30, pady=10)
        new_btn.pack(side="left", padx=20)
    
    def reset_and_restart(self):
        """
        Reset the application state to begin a completely new test.
        Clears the current session data and returns to the gender selection screen.
        """
        self.current_scenario_index = 0
        self.session = None
        self.waiting_for_break = False
        self.show_gender_selection()


def main():
    """Entry point of the application."""
    app = TrustAssessmentApp()
    app.run()


# If this script is executed directly (not imported), run the main function.
if __name__ == "__main__":
    main()