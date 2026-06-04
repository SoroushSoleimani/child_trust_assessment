import tkinter as tk
from ..utils.config import WINDOW_WIDTH, WINDOW_HEIGHT, BACKGROUND_COLOR, BREAK_DURATION_SECONDS

# ============================================================================
# BREAK WINDOW UI COMPONENT
# ============================================================================
# This module implements a rest break screen that appears after the 4th scenario
# (halfway through the test). It gives the child a short pause before continuing
# with the remaining scenarios. The window includes a countdown timer and a
# "skip" button to allow the test administrator or child to bypass the rest period.

class BreakWindow:
    """
    A top-level window that displays a break screen with a countdown timer.
    
    The break window is shown automatically after completing the first 4 scenarios.
    It gives the child a short rest (default duration defined in config.py).
    The user can either wait for the timer to expire or click the "skip" button
    to resume the test immediately.
    
    Attributes:
        parent (tk.Tk or tk.Toplevel): The parent window (usually the main root or a Toplevel).
        on_complete (callable): A callback function to execute when the break ends
            (either by timer or skip). This typically resumes the test by showing the next video.
        remaining (int): Seconds left in the break countdown.
        after_id (str or None): Identifier for the `after()` scheduled callback,
            used to cancel the timer if the user skips.
        skipped (bool): Flag indicating whether the break has been skipped,
            prevents double triggering.
    """
    
    def __init__(self, parent, on_complete):
        """
        Initialize the break window, set up its appearance, and start the timer.
        
        Args:
            parent (tk.Tk or tk.Toplevel): The parent window that will host this break screen.
            on_complete (callable): Function to call when the break finishes (no arguments).
        """
        self.parent = parent
        self.on_complete = on_complete
        
        # Get break duration from config (e.g., 30 seconds)
        self.remaining = BREAK_DURATION_SECONDS
        
        self.after_id = None      # Will store the scheduled `after` task ID
        self.skipped = False      # Track if skip button was pressed
        
        # Configure the parent window (which is typically a Toplevel created by the main app)
        self.parent.title("زمان استراحت")                         # Persian title: "Rest Time"
        self.parent.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")  # Set window size (e.g., 1024x768)
        self.parent.configure(bg=BACKGROUND_COLOR)               # Use background color from config
        
        # Create all UI elements (labels, timer display, skip button)
        self._create_widgets()
        
        # Start the countdown timer
        self._start_timer()
    
    def _create_widgets(self):
        """
        Build the user interface for the break window.
        
        This includes:
            - A main frame to center all elements
            - A title label ("Rest Time")
            - A message label ("You can take a short break")
            - A timer label showing remaining seconds
            - A skip button to bypass the break
        """
        # Main frame – expands to fill the window and centers its contents
        main_frame = tk.Frame(self.parent, bg=BACKGROUND_COLOR)
        main_frame.pack(expand=True)
        
        # Title label (large Persian font)
        title = tk.Label(main_frame, text="زمان استراحت", 
                         font=("B Titr", 28), bg=BACKGROUND_COLOR, fg="white")
        title.pack(pady=50)
        
        # Informational message (smaller font, gold color for emphasis)
        message = tk.Label(main_frame, text="می‌توانی کمی استراحت کنی", 
                           font=("B Nazanin", 18), bg=BACKGROUND_COLOR, fg="#FFD700")
        message.pack(pady=20)
        
        # Timer label – will be updated every second
        self.timer_label = tk.Label(main_frame, text=f"زمان باقی‌مانده: {self.remaining} ثانیه", 
                                     font=("B Nazanin", 24), bg=BACKGROUND_COLOR, fg="white")
        self.timer_label.pack(pady=40)
        
        # Skip button – allows immediate continuation
        skip_btn = tk.Button(main_frame, text="رد کردن استراحت", 
                             command=self._skip, font=("B Nazanin", 14), 
                             bg="#FF9800", fg="white", padx=30, pady=10)
        skip_btn.pack(pady=20)
    
    def _start_timer(self):
        """
        Start the countdown by scheduling the first `_update_timer` call.
        """
        self._update_timer()
    
    def _update_timer(self):
        """
        Update the timer label every second and decrement the remaining counter.
        When the counter reaches zero, the break ends.
        If the break was already skipped, do nothing.
        """
        if self.skipped:
            return
        
        if self.remaining <= 0:
            # Time's up – finish the break
            self._finish()
        else:
            # Update the label with current remaining time
            self.timer_label.config(text=f"زمان باقی‌مانده: {self.remaining} ثانیه")
            self.remaining -= 1
            # Schedule the next update after 1000 ms (1 second)
            self.after_id = self.parent.after(1000, self._update_timer)
    
    def _skip(self):
        """
        Handle the "Skip Break" button click.
        
        Cancels the timer if it is running, marks the break as skipped,
        and immediately finishes the break (calls `_finish`).
        """
        if self.skipped:
            return
        
        self.skipped = True
        
        # Cancel any pending timer updates to prevent further countdown
        if self.after_id:
            self.parent.after_cancel(self.after_id)
        
        # Proceed to finish the break (call the callback)
        self._finish()
    
    def _finish(self):
        """
        Close the break window and execute the `on_complete` callback.
        
        This method is called either when the timer expires or when the
        skip button is clicked. It destroys the Toplevel window and then
        invokes the callback (typically to resume the test with the next video).
        """
        self.parent.destroy()   # Close this break window
        self.on_complete()      # Notify the main application that break is over