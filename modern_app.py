import flet as ft
import subprocess
import sys
import os

# ============================================================================
# FLET LAUNCHER APPLICATION - TRUST ASSESSMENT TEST
# ============================================================================
# This module serves as a simple launcher for the main Trust Assessment application.
# It displays a gender selection screen using the Flet framework, and when the user
# clicks either "Girls" or "Boys", it launches the main application (run.py) as a
# separate subprocess. This allows the launcher to remain lightweight and close
# independently of the main test window.
#
# Note: This approach is useful when you want a simple splash/launcher that
# starts the full application in a separate process. The main application
# (run.py) is assumed to be in the same directory as this script.

def main(page: ft.Page):
    """
    Build and display the launcher window with gender selection buttons.
    
    Args:
        page (ft.Page): The root page object provided by the Flet runtime.
    """
    # Configure the window properties
    page.title = "آزمون سنجش اعتماد کودکان"          # Persian: "Child Trust Assessment Test"
    page.theme_mode = ft.ThemeMode.LIGHT           # Use light color theme
    page.bgcolor = ft.Colors.WHITE                 # White background
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER   # Center content horizontally
    page.vertical_alignment = ft.MainAxisAlignment.CENTER       # Center content vertically
    page.window_width = 800                        # Window width in pixels
    page.window_height = 600                       # Window height in pixels

    # Title label at the top
    title = ft.Text("آزمون سنجش اعتماد کودکان", size=40, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800)
    
    # Subtitle instruction text
    subtitle = ft.Text("لطفاً جنسیت خود را انتخاب کنید", size=20, color=ft.Colors.GREY_600)
    
    # ------------------------------------------------------------------------
    # EVENT HANDLERS FOR GENDER BUTTONS
    # ------------------------------------------------------------------------
    def start_girl(e):
        """
        Callback for the "Girls" button. Launches the main test application
        (run.py) as a subprocess. Prints status messages to console.
        
        Args:
            e: The click event (not used).
        """
        print("شروع تست دختران")   # Persian: "Starting girls test"
        try:
            # Get the directory where this script is located
            script_dir = os.path.dirname(__file__)
            # Path to the main application script (run.py)
            original_file = os.path.join(script_dir, "run.py")
            # Launch run.py as a separate process using the same Python interpreter
            subprocess.Popen([sys.executable, original_file])
        except Exception as ex:
            print(f"خطا: {ex}")   # Persian: "Error: {ex}"
    
    def start_boy(e):
        """
        Callback for the "Boys" button. Launches the main test application
        (run.py) as a subprocess. Prints status messages to console.
        
        Args:
            e: The click event (not used).
        """
        print("شروع تست پسران")    # Persian: "Starting boys test"
        try:
            script_dir = os.path.dirname(__file__)
            original_file = os.path.join(script_dir, "run.py")
            subprocess.Popen([sys.executable, original_file])
        except Exception as ex:
            print(f"خطا: {ex}")

    # ------------------------------------------------------------------------
    # UI BUTTONS
    # ------------------------------------------------------------------------
    # Button for girls – pink background, large text
    girl_button = ft.ElevatedButton(
        content=ft.Text("دختران", size=24, weight=ft.FontWeight.BOLD),
        on_click=start_girl,
        width=200,
        height=80,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.PINK_400,
        )
    )
    
    # Button for boys – blue background, large text
    boy_button = ft.ElevatedButton(
        content=ft.Text("پسران", size=24, weight=ft.FontWeight.BOLD),
        on_click=start_boy,
        width=200,
        height=80,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE_400,
        )
    )

    # ------------------------------------------------------------------------
    # LAYOUT - ARRANGE ALL CONTROLS VERTICALLY
    # ------------------------------------------------------------------------
    page.add(
        ft.Column(
            [
                title,                        # Main title
                ft.Container(height=30),      # Vertical spacer
                subtitle,                     # Instruction text
                ft.Container(height=50),
                ft.Row([girl_button, boy_button], alignment=ft.MainAxisAlignment.CENTER, spacing=50),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )

# ----------------------------------------------------------------------------
# ENTRY POINT
# ----------------------------------------------------------------------------
# Run the Flet application with the main function as the target.
ft.app(target=main)