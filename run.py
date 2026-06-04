import sys
import os

# ============================================================================
# APPLICATION LAUNCHER / PATH CONFIGURATOR
# ============================================================================
# This script acts as the main entry point for the Trust Assessment application.
# It ensures that the 'src' directory (which contains the main package) is
# added to Python's module search path, allowing the application to import
# modules from the 'trust_assessment' package regardless of the current
# working directory. After configuring the path, it imports the main function
# from the trust_assessment.main module and executes it.

# ----------------------------------------------------------------------------
# STEP 1: MODIFY PYTHON MODULE SEARCH PATH (sys.path)
# ----------------------------------------------------------------------------
# When the application is run, Python looks for modules in directories listed
# in sys.path. By default, this includes the script's directory and system
# site-packages. However, the main application package ('trust_assessment')
# resides inside the 'src' folder. To make it importable, we prepend the
# absolute path of 'src' to sys.path.

# Get the directory where this script (the launcher) is located.
script_dir = os.path.dirname(__file__)

# Construct the path to the 'src' folder relative to the script directory.
# Assuming the following structure:
#   project_root/
#       launcher.py (this file)
#       src/
#           trust_assessment/
#               main.py
#               ... other modules
src_path = os.path.join(script_dir, "src")

# Insert the 'src' path at the beginning of sys.path (position 0).
# This gives it the highest priority, ensuring that any import of
# 'trust_assessment' resolves to the local src/trust_assessment folder
# rather than any globally installed package with the same name.
sys.path.insert(0, src_path)

# ----------------------------------------------------------------------------
# STEP 2: IMPORT AND RUN THE MAIN APPLICATION
# ----------------------------------------------------------------------------
# After the path is configured, we can import the main function from the
# trust_assessment.main module. This module contains the core application
# logic (e.g., the TrustAssessmentApp class and its run method).
from trust_assessment.main import main

# ----------------------------------------------------------------------------
# STEP 3: EXECUTE THE APPLICATION WHEN THIS SCRIPT IS RUN DIRECTLY
# ----------------------------------------------------------------------------
# The standard Python idiom: if this script is executed directly (not imported
# as a module), call the main() function to start the test application.
if __name__ == "__main__":
    main()