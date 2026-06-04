import sys
import os
from cx_Freeze import setup, Executable

base = None
if sys.platform == "win32":
    base = "Win32GUI"

build_exe_options = {
    "packages": ["customtkinter", "tkinter", "pandas", "openpyxl", "PIL", "cv2", "random", "datetime", "os", "subprocess"],
    "include_files": [
        ("ctk_app.py", "ctk_app.py"),
        ("src", "src"),
        ("data", "data")
    ],
    "excludes": [],
    "include_msvcr": True,
}

setup(
    name="TrustAssessmentApp",
    version="1.0",
    description="آزمون سنجش اعتماد کودکان",
    options={"build_exe": build_exe_options},
    executables=[Executable("run_exe.py", base=base, icon=None, target_name="TrustAssessmentApp.exe")]
)