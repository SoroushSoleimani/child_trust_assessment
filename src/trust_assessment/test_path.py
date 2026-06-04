import os

# ============================================================================
# PATH TESTING SCRIPT - VERIFY DIRECTORY STRUCTURE
# ============================================================================
# This script is used for debugging and verification purposes.
# It calculates the project root directory based on the current file's location,
# constructs the expected paths for video folders (boys/girls), and checks
# whether those directories exist. It also lists the contents of the 'boys'
# folder if available.
#
# This helps ensure that the application's path configuration is correct
# and that all required video files are present.

# Print a header for the test output
print("=== تست مسیرها ===\n")

# ----------------------------------------------------------------------------
# GET CURRENT FILE PATH
# ----------------------------------------------------------------------------
# __file__ is the full path of the current Python script.
# os.path.abspath() ensures we have an absolute path (resolves any relative parts).
current_file = os.path.abspath(__file__)
print("مسیر فایل فعلی:", current_file)

# ----------------------------------------------------------------------------
# CALCULATE ROOT DIRECTORY
# ----------------------------------------------------------------------------
# The project structure is assumed to be:
#   root/
#       src/
#           trust_assessment/
#               utils/
#                   config.py               (this script might be here)
#               ... other modules
#       data/
#       ...
#
# To get the root directory, we go up three levels from the current file:
#   current_file = root/src/trust_assessment/utils/test_paths.py (example)
#   dirname(current_file) -> root/src/trust_assessment/utils
#   dirname(dirname(current_file)) -> root/src/trust_assessment
#   dirname(dirname(dirname(current_file))) -> root/src
#   Actually, the code uses three os.path.dirname calls to go up three levels.
#   This assumes the script is located at: ROOT_DIR/src/trust_assessment/utils/<this_file>.
#   Adjust if the file is placed elsewhere.
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
print("ROOT_DIR محاسبه شده:", ROOT_DIR)

# ----------------------------------------------------------------------------
# BUILD VIDEO DIRECTORY PATHS
# ----------------------------------------------------------------------------
# Construct the full path to the videos directory based on the calculated ROOT_DIR.
VIDEOS_DIR = os.path.join(ROOT_DIR, "src", "trust_assessment", "assets", "videos")
print("VIDEOS_DIR:", VIDEOS_DIR)

# Path to the folder containing videos for girl scenarios
GIRLS_DIR = os.path.join(VIDEOS_DIR, "girls")
print("GIRLS_DIR:", GIRLS_DIR)
print("آیا وجود دارد؟", os.path.exists(GIRLS_DIR))   # Check existence

# Path to the folder containing videos for boy scenarios
BOYS_DIR = os.path.join(VIDEOS_DIR, "boys")
print("BOYS_DIR:", BOYS_DIR)
print("آیا وجود دارد؟", os.path.exists(BOYS_DIR))

# ----------------------------------------------------------------------------
# LIST FILES IN BOYS DIRECTORY (IF EXISTS)
# ----------------------------------------------------------------------------
print("\n=== لیست فایل‌های boys ===")
if os.path.exists(BOYS_DIR):
    # Iterate over all entries in the boys directory and print their names
    for f in os.listdir(BOYS_DIR):
        print(f)
else:
    print("پوشه وجود ندارد!")   # Folder does not exist