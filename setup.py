import sys
import os
from cx_Freeze import setup, Executable

# ============================================================================
# BUILD CONFIGURATION FOR CX_FREEZE (CREATING STANDALONE EXECUTABLE)
# ============================================================================
# This script is used to package the Trust Assessment application into a
# standalone .exe file for Windows. It uses cx_Freeze to bundle the Python
# interpreter, required modules, and additional data files.

# ----------------------------------------------------------------------------
# DETERMINE THE BASE TARGET FOR THE EXECUTABLE
# ----------------------------------------------------------------------------
# 'base' defines the type of application. For Windows GUI applications (no
# console window), we set base = "Win32GUI". On other platforms, base remains
# None, which will show a console window (useful for debugging).
base = None
if sys.platform == "win32":
    base = "Win32GUI"   # Prevents a terminal window from appearing when the app runs

# ----------------------------------------------------------------------------
# BUILD OPTIONS DICTIONARY
# ----------------------------------------------------------------------------
# This dictionary configures how cx_Freeze builds the executable.
build_exe_options = {
    # "packages": List of Python packages that must be included explicitly.
    # cx_Freeze automatically detects imports, but some packages (like
    # customtkinter, pandas, openpyxl, etc.) may need to be listed to ensure
    # all submodules are bundled correctly.
    "packages": [
        "customtkinter",    # Modern UI toolkit
        "tkinter",          # Standard GUI (used internally by customtkinter)
        "pandas",           # Data manipulation (reading/writing Excel files)
        "openpyxl",         # Excel engine for pandas
        "PIL",              # Python Imaging Library (for background images)
        "cv2",              # OpenCV (if used for video processing; here for completeness)
        "random",           # Random scenario ordering and participant codes
        "datetime",         # Timestamp for saving files
        "os",               # Operating system interface (file paths, checks)
        "subprocess"        # For running external processes if needed
    ],
    
    # "include_files": List of additional files/directories to copy into the
    # build folder. These are not Python modules but are required at runtime.
    "include_files": [
        ("ctk_app.py", "ctk_app.py"),   # Main application script (if needed)
        ("src", "src"),                 # Entire source directory (contains trust_assessment package)
        ("data", "data")                # Data folder (contains scoring_keys.xlsx)
    ],
    
    # "excludes": List of modules to explicitly exclude (reduces build size).
    "excludes": [],
    
    # "include_msvcr": Include Microsoft Visual C++ Redistributable DLLs.
    # This is important for Windows to avoid missing runtime DLL errors.
    "include_msvcr": True,
}

# ----------------------------------------------------------------------------
# SETUP CONFIGURATION
# ----------------------------------------------------------------------------
setup(
    name="TrustAssessmentApp",               # Name of the application
    version="1.0",                            # Version number
    description="آزمون سنجش اعتماد کودکان",  # Persian description: "Child Trust Assessment Test"
    
    # Pass the build options defined above
    options={"build_exe": build_exe_options},
    
    # Define the executable(s) to create. 'run_exe.py' is the entry point script.
    # The 'base' determines GUI vs console, and 'target_name' sets the output .exe filename.
    executables=[Executable("run_exe.py", base=base, icon=None, target_name="TrustAssessmentApp.exe")]
)