import os
import sys
import subprocess

# ============================================================================
# RESOURCE PATH RESOLVER FOR PACKAGED APPLICATIONS (PyInstaller / cx_Freeze)
# ============================================================================
# This script serves as a launcher for the main application (ctk_app.py).
# It is designed to work correctly both when run as a normal Python script
# and when the application is packaged into a standalone executable using
# tools like PyInstaller or cx_Freeze.
#
# The key challenge: When packaged, data files (including Python scripts)
# are extracted to a temporary folder (sys._MEIPASS for PyInstaller).
# This function provides a unified way to get the correct path regardless
# of execution environment.

def resource_path(relative_path):
    """
    Get the absolute path to a resource, compatible with both development
    and packaged (frozen) execution modes.
    
    When the application is frozen (packaged into an .exe), the resources
    are stored in a temporary directory pointed to by sys._MEIPASS.
    When running as a normal script, resources are relative to the current
    working directory.
    
    Args:
        relative_path (str): The relative path to the resource file or folder.
        
    Returns:
        str: Absolute path to the resource, suitable for use with file operations.
    
    Example:
        >>> path = resource_path("ctk_app.py")
        >>> # Returns: "C:\\temp\\_MEIxxxxx\\ctk_app.py" when frozen
        >>> # or "./ctk_app.py" when in development.
    """
    try:
        # Check if we are running in a frozen (packaged) environment.
        # sys._MEIPASS is set by PyInstaller and cx_Freeze (with appropriate hooks).
        base_path = sys._MEIPASS
    except Exception:
        # Not frozen: use the current working directory (where the script resides).
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


if __name__ == "__main__":
    """
    Entry point of the launcher.
    
    When this script is executed directly, it locates the main application
    file (ctk_app.py) using resource_path(), then runs it as a subprocess
    using the same Python interpreter. This approach ensures that any
    resources (images, videos, data files) are correctly resolved even
    after the application has been packaged into an executable.
    """
    # Get the correct path to the main application script
    ctk_app_path = resource_path("ctk_app.py")
    
    # Launch the main application in a separate subprocess.
    # Using subprocess.run() blocks until the main app exits, which is fine
    # for a launcher. The same Python interpreter is used.
    subprocess.run([sys.executable, ctk_app_path])