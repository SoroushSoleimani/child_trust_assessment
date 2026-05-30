import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from ..models.participant import Participant
from ..utils.config import WINDOW_WIDTH, WINDOW_HEIGHT, BACKGROUND_COLOR

class EntryWindow:
    
    def __init__(self, parent, on_submit, gender_selection=True):
        self.parent = parent
        self.on_submit = on_submit
        self.gender_selection = gender_selection
        self.result = None
        
        self.parent.title("فرم ثبت اطلاعات")
        self.parent.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.parent.configure(bg=BACKGROUND_COLOR)
        
        self._create_widgets()
    
    def _create_widgets(self):
        main_frame = tk.Frame(self.parent, bg=BACKGROUND_COLOR)
        main_frame.pack(expand=True)
        
        title = tk.Label(main_frame, text="آزمون سنجش اعتماد کودکان", 
                         font=("B Titr", 24, "bold"), bg=BACKGROUND_COLOR, fg="white")
        title.pack(pady=30)
        
        form_frame = tk.Frame(main_frame, bg="white", padx=40, pady=40)
        form_frame.pack(pady=20)
        
        row = 0
        tk.Label(form_frame, text="نام و نام خانوادگی:", font=("B Nazanin", 14), bg="white").grid(row=row, column=0, pady=10, sticky="e")
        self.name_entry = tk.Entry(form_frame, font=("B Nazanin", 14), width=30)
        self.name_entry.grid(row=row, column=1, pady=10, padx=10)
        
        row += 1
        tk.Label(form_frame, text="سن:", font=("B Nazanin", 14), bg="white").grid(row=row, column=0, pady=10, sticky="e")
        self.age_entry = tk.Entry(form_frame, font=("B Nazanin", 14), width=10)
        self.age_entry.grid(row=row, column=1, pady=10, padx=10, sticky="w")
        
        row += 1
        tk.Label(form_frame, text="پایه تحصیلی:", font=("B Nazanin", 14), bg="white").grid(row=row, column=0, pady=10, sticky="e")
        self.grade_combo = ttk.Combobox(form_frame, values=["اول", "دوم"], font=("B Nazanin", 14), width=15)
        self.grade_combo.grid(row=row, column=1, pady=10, padx=10, sticky="w")
        
        if self.gender_selection:
            row += 1
            tk.Label(form_frame, text="جنسیت:", font=("B Nazanin", 14), bg="white").grid(row=row, column=0, pady=10, sticky="e")
            self.gender_var = tk.StringVar()
            gender_frame = tk.Frame(form_frame, bg="white")
            gender_frame.grid(row=row, column=1, pady=10, padx=10, sticky="w")
            tk.Radiobutton(gender_frame, text="دختر", variable=self.gender_var, value="girl", 
                          font=("B Nazanin", 12), bg="white").pack(side="left", padx=10)
            tk.Radiobutton(gender_frame, text="پسر", variable=self.gender_var, value="boy", 
                          font=("B Nazanin", 12), bg="white").pack(side="left", padx=10)
        
        row += 1
        btn_frame = tk.Frame(form_frame, bg="white")
        btn_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        submit_btn = tk.Button(btn_frame, text="شروع آزمایش", command=self._submit,
                               font=("B Nazanin", 14), bg=BACKGROUND_COLOR, fg="white", padx=30, pady=10)
        submit_btn.pack()
    
    def _submit(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("خطا", "لطفاً نام و نام خانوادگی را وارد کنید")
            return
        
        try:
            age = int(self.age_entry.get().strip())
        except:
            messagebox.showerror("خطا", "لطفاً سن را به درستی وارد کنید")
            return
        
        grade = self.grade_combo.get()
        if not grade:
            messagebox.showerror("خطا", "لطفاً پایه تحصیلی را انتخاب کنید")
            return
        
        gender = None
        if self.gender_selection:
            gender = self.gender_var.get()
            if not gender:
                messagebox.showerror("خطا", "لطفاً جنسیت را انتخاب کنید")
                return
        else:
            gender = "unknown"
        
        participant = Participant(
            code=0,
            name=name,
            age=age,
            grade=grade,
            gender=gender,
            session_date=datetime.now().strftime("%Y-%m-%d"),
            session_time=datetime.now().strftime("%H:%M:%S")
        )
        
        self.result = participant
        self.on_submit(participant)