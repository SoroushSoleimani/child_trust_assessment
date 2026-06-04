import os

# ============================================================================
# CONFIGURATION FILE - TRUST ASSESSMENT APPLICATION
# ============================================================================
# This module contains all global configuration settings for the Child Trust
# Assessment Test application. It defines paths, constants, UI dimensions,
# video settings, break duration, scenario names, questions, and answer options.
#
# All other modules import from this file to access shared settings,
# ensuring consistency across the application.

# ----------------------------------------------------------------------------
# FILE SYSTEM PATHS
# ----------------------------------------------------------------------------
# ROOT_DIR: Absolute path to the project root directory.
# This should point to the base folder of the application.
# Using raw string (r"") to avoid escape sequence issues on Windows.
ROOT_DIR = r"E:\child_trust_assessment"

# VIDEOS_DIR: Directory containing all video assets.
# Videos are organized by gender subfolders ("girls" and "boys").
VIDEOS_DIR = os.path.join(ROOT_DIR, "src", "trust_assessment", "assets", "videos")

# GIRLS_VIDEOS_DIR: Videos for scenarios where the speaker is a girl.
GIRLS_VIDEOS_DIR = os.path.join(VIDEOS_DIR, "girls")

# BOYS_VIDEOS_DIR: Videos for scenarios where the speaker is a boy.
BOYS_VIDEOS_DIR = os.path.join(VIDEOS_DIR, "boys")

# DATA_DIR: Directory where the Excel output files will be saved.
# This includes the scoring_keys.xlsx file (which contains the gold standard
# answers and scoring rubrics) and future participant response files.
DATA_DIR = os.path.join(ROOT_DIR, "data", "raw")

# SCORING_KEYS_FILE: Full path to the Excel file that contains:
#   - Sheet1: Participant raw responses
#   - Sheet2: Gold standard answers and scoring keys (mistrust/trust/gullibility)
#   - Sheet3: Aggregated scores
SCORING_KEYS_FILE = os.path.join(DATA_DIR, "scoring_keys.xlsx")

# ----------------------------------------------------------------------------
# WINDOW GEOMETRY AND APPEARANCE
# ----------------------------------------------------------------------------
# WINDOW_WIDTH: Default width for all application windows (main, entry, video, questions).
WINDOW_WIDTH = 1024

# WINDOW_HEIGHT: Default height for all application windows.
WINDOW_HEIGHT = 768

# BACKGROUND_COLOR: Default background color (hex code) used for windows and frames.
# The color is a dark green (#2E7D64) that creates a calm, child-friendly interface.
BACKGROUND_COLOR = "#2E7D64"

# ----------------------------------------------------------------------------
# VIDEO SETTINGS
# ----------------------------------------------------------------------------
# VIDEO_EXTENSIONS: List of supported video file extensions.
# The application will look for these extensions when scanning video folders.
# .mp4 is the primary format, but others are supported as fallbacks.
VIDEO_EXTENSIONS = [".mp4", ".MP4", ".avi", ".AVI", ".mov", ".MOV", ".mkv", ".MKV"]

# BREAK_DURATION_SECONDS: Length of the rest break (in seconds) shown after the
# 4th scenario (midway through the test). The child can wait or skip.
BREAK_DURATION_SECONDS = 30

# ----------------------------------------------------------------------------
# SCENARIO NAMES
# ----------------------------------------------------------------------------
# SENARIO_NAMES: List of all 8 scenario identifiers.
# Each scenario corresponds to a video file and a set of questions.
# The order is randomized for each test session to reduce bias.
SENARIO_NAMES = ["SEN1", "SEN2", "SEN3", "SEN4", "SEN5", "SEN6", "SEN7", "SEN8"]

# ----------------------------------------------------------------------------
# QUESTIONS
# ----------------------------------------------------------------------------
# QUESTIONS: List of dictionaries defining the 4 questions asked after each video.
# Each dictionary contains:
#   - "key": Internal identifier used in code and Excel columns (e.g., "correctness").
#   - "text": The question text in Persian as displayed to the child.
#
# Order matters: The questions are displayed in the same order as listed here.
# Keys correspond to Excel columns (e.g., "SEN1-CO" for correctness, "SEN1-NIC" for niceness).
QUESTIONS = [
    {"key": "correctness", "text": "به نظرت چقدر از جوابای این پسر/دختر درست بود؟"},
    {"key": "niceness", "text": "به نظرات این پسر/دختر خوبیه؟"},
    {"key": "trust", "text": "به نظرت تو چقدر از حرفای این پسر/دختر رو قبول می‌کنی؟"},
    {"key": "self_disclosure", "text": "به نظرات تو رازهای خودتو به این پسر/دختر میگی؟"},
]

# ----------------------------------------------------------------------------
# ANSWER OPTIONS
# ----------------------------------------------------------------------------
# ANSWER_OPTIONS: List of Persian text labels for the 5 answer choices.
# These correspond to the Likert scale from 1 (lowest trust/agreement) to 5 (highest).
# The order is important: index 0 = "هیچکدوم" (none), index 4 = "همه‌ش" (all).
ANSWER_OPTIONS = [
    "هیچکدوم",        # 1 - None / Not at all
    "فقط یه کوچولو",   # 2 - Just a little
    "نصفش",           # 3 - Half of it
    "بیشترش",         # 4 - Most of it
    "همه‌ش",          # 5 - All of it
]

# ANSWER_MAPPING: Dictionary mapping each Persian answer text to its numeric value (1-5).
# This is used to convert the selected text option to an integer for storage and scoring.
# For example: ANSWER_MAPPING["نصفش"] returns 3.
ANSWER_MAPPING = {text: idx + 1 for idx, text in enumerate(ANSWER_OPTIONS)}