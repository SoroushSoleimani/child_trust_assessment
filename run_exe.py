import os
import sys
import subprocess

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    ctk_app_path = resource_path("ctk_app.py")
    subprocess.run([sys.executable, ctk_app_path])