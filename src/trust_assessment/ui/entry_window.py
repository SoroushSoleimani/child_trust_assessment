import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from ..models.participant import Participant
from ..utils.config import WINDOW_WIDTH, WINDOW_HEIGHT, BACKGROUND_COLOR

# ============================================================================
# PARTICIPANT INFORMATION ENTRY WINDOW
# ============================================================================
# This module provides a GUI form for collecting demographic information about
# the child before starting the trust assessment test. It collects name, age,
# grade, and optionally gender (if not already selected in a previous screen).
# After validation, it creates a Participant object and passes it to a callback.

class EntryWindow:
    """
    A Tkinter window that displays a form for entering participant details.
    
    The form includes:
        - Full name (text entry)
        - Age (numeric entry)
        - Grade (dropdown with Persian grade levels)
        - Gender (radio buttons, if gender_selection is True)
    
    After the user fills the form and clicks "Start Test", validation is performed.
    If all fields are valid, a Participant object is created and the on_submit
    callback is invoked with that object.
    
    Attributes:
        parent (tk.Tk or tk.Toplevel): The parent window that hosts this form.
        on_submit (callable): Callback function that receives the Participant object.
        gender_selection (bool): If True, show gender radio buttons; otherwise,
            gender will be set to "unknown" (used when gender was already chosen).
        result (Participant or None): Stores the created Participant object.
        name_entry (tk.Entry): Entry widget for the child's full name.
        age_entry (tk.Entry): Entry widget for the child's age.
        grade_combo (ttk.Combobox): Dropdown for selecting school grade.
        gender_var (tk.StringVar): Variable holding the selected gender ("girl"/"boy").
    """
    
    def __init__(self, parent, on_submit, gender_selection=True):
        """
        Initialize the entry window, set up the UI, and prepare for data entry.
        
        Args:
            parent (tk.Tk or tk.Toplevel): The parent window (usually the main root).
            on_submit (callable): Function to call when form is submitted.
                It should accept one argument: a Participant object.
            gender_selection (bool): Whether to display gender radio buttons.
                Default is True. Set to False if gender was already chosen
                (e.g., from a previous gender selection screen).
        """
        self.parent = parent
        self.on_submit = on_submit
        self.gender_selection = gender_selection
        self.result = None          # Will hold the created Participant object
        
        # Configure the parent window appearance
        self.parent.title("فرم ثبت اطلاعات")                       # Persian: "Information Registration Form"
        self.parent.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")   # Set window size from config
        self.parent.configure(bg=BACKGROUND_COLOR)                # Set background color
        
        # Build all UI widgets
        self._create_widgets()
    
    def _create_widgets(self):
        """
        Create and arrange all graphical elements of the entry form.
        
        The layout uses a main frame for centering, a white form frame,
        and grid geometry inside the form frame for labels and inputs.
        """
        # Main frame – expands to fill the window, holds everything
        main_frame = tk.Frame(self.parent, bg=BACKGROUND_COLOR)
        main_frame.pack(expand=True)
        
        # Title label at the top
        title = tk.Label(main_frame, text="آزمون سنجش اعتماد کودکان", 
                         font=("B Titr", 24, "bold"), bg=BACKGROUND_COLOR, fg="white")
        title.pack(pady=30)
        
        # White frame that contains the actual form (looks like a card)
        form_frame = tk.Frame(main_frame, bg="white", padx=40, pady=40)
        form_frame.pack(pady=20)
        
        # Row counter for grid placement
        row = 0
        
        # --- Full Name field ---
        tk.Label(form_frame, text="نام و نام خانوادگی:", font=("B Nazanin", 14), bg="white")\
            .grid(row=row, column=0, pady=10, sticky="e")
        self.name_entry = tk.Entry(form_frame, font=("B Nazanin", 14), width=30)
        self.name_entry.grid(row=row, column=1, pady=10, padx=10)
        
        # --- Age field ---
        row += 1
        tk.Label(form_frame, text="سن:", font=("B Nazanin", 14), bg="white")\
            .grid(row=row, column=0, pady=10, sticky="e")
        self.age_entry = tk.Entry(form_frame, font=("B Nazanin", 14), width=10)
        self.age_entry.grid(row=row, column=1, pady=10, padx=10, sticky="w")
        
        # --- Grade dropdown ---
        row += 1
        tk.Label(form_frame, text="پایه تحصیلی:", font=("B Nazanin", 14), bg="white")\
            .grid(row=row, column=0, pady=10, sticky="e")
        # Values are Persian grade levels: "اول" (first), "دوم" (second), etc.
        self.grade_combo = ttk.Combobox(form_frame, values=["اول", "دوم"], 
                                        font=("B Nazanin", 14), width=15)
        self.grade_combo.grid(row=row, column=1, pady=10, padx=10, sticky="w")
        
        # --- Gender selection (optional) ---
        if self.gender_selection:
            row += 1
            tk.Label(form_frame, text="جنسیت:", font=("B Nazanin", 14), bg="white")\
                .grid(row=row, column=0, pady=10, sticky="e")
            self.gender_var = tk.StringVar()   # Will hold "girl" or "boy"
            gender_frame = tk.Frame(form_frame, bg="white")
            gender_frame.grid(row=row, column=1, pady=10, padx=10, sticky="w")
            # Girl radio button
            tk.Radiobutton(gender_frame, text="دختر", variable=self.gender_var, value="girl", 
                          font=("B Nazanin", 12), bg="white").pack(side="left", padx=10)
            # Boy radio button
            tk.Radiobutton(gender_frame, text="پسر", variable=self.gender_var, value="boy", 
                          font=("B Nazanin", 12), bg="white").pack(side="left", padx=10)
        
        # --- Submit button ---
        row += 1
        btn_frame = tk.Frame(form_frame, bg="white")
        btn_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        submit_btn = tk.Button(btn_frame, text="شروع آزمایش", command=self._submit,
                               font=("B Nazanin", 14), bg=BACKGROUND_COLOR, fg="white", 
                               padx=30, pady=10)
        submit_btn.pack()
    
    def _submit(self):
        """
        Validate the entered data and create a Participant object.
        
        This method is called when the user clicks the "Start Test" button.
        It performs the following validations:
            - Name must not be empty.
            - Age must be a valid integer.
            - Grade must be selected from the dropdown.
            - If gender_selection is True, a gender must be chosen.
        
        If validation passes, a Participant object is created (code is set to 0
        temporarily; it will be assigned later). The current date and time are
        stored. Then the on_submit callback is invoked with the participant object.
        
        If validation fails, an error messagebox is shown and submission is aborted.
        """
        # Validate name
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("خطا", "لطفاً نام و نام خانوادگی را وارد کنید")
            return
        
        # Validate age (must be integer)
        try:
            age = int(self.age_entry.get().strip())
        except:
            messagebox.showerror("خطا", "لطفاً سن را به درستی وارد کنید")
            return
        
        # Validate grade (must be selected)
        grade = self.grade_combo.get()
        if not grade:
            messagebox.showerror("خطا", "لطفاً پایه تحصیلی را انتخاب کنید")
            return
        
        # Validate gender if required
        gender = None
        if self.gender_selection:
            gender = self.gender_var.get()
            if not gender:
                messagebox.showerror("خطا", "لطفاً جنسیت را انتخاب کنید")
                return
        else:
            gender = "unknown"   # Placeholder when gender was already selected elsewhere
        
        # Create Participant object (code will be assigned later by the main app)
        participant = Participant(
            code=0,                                          # Temporary code
            name=name,
            age=age,
            grade=grade,
            gender=gender,
            session_date=datetime.now().strftime("%Y-%m-%d"),  # Today's date
            session_time=datetime.now().strftime("%H:%M:%S")   # Current time
        )
        
        # Store the participant and call the callback
        self.result = participant
        self.on_submit(participant)