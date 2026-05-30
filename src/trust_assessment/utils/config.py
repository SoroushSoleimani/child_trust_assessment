import os

ROOT_DIR = r"E:\child_trust_assessment"

VIDEOS_DIR = os.path.join(ROOT_DIR, "src", "trust_assessment", "assets", "videos")
GIRLS_VIDEOS_DIR = os.path.join(VIDEOS_DIR, "girls")
BOYS_VIDEOS_DIR = os.path.join(VIDEOS_DIR, "boys")

DATA_DIR = os.path.join(ROOT_DIR, "data", "raw")

SCORING_KEYS_FILE = os.path.join(DATA_DIR, "scoring_keys.xlsx")

WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
BACKGROUND_COLOR = "#2E7D64"

VIDEO_EXTENSIONS = [".mp4", ".MP4", ".avi", ".AVI", ".mov", ".MOV", ".mkv", ".MKV"]

BREAK_DURATION_SECONDS = 30

SENARIO_NAMES = ["SEN1", "SEN2", "SEN3", "SEN4", "SEN5", "SEN6", "SEN7", "SEN8"]

QUESTIONS = [
    {"key": "correctness", "text": "به نظرت چقدر از جوابای این پسر/دختر درست بود؟"},
    {"key": "niceness", "text": "به نظرات این پسر/دختر خوبیه؟"},
    {"key": "trust", "text": "به نظرت تو چقدر از حرفای این پسر/دختر رو قبول می‌کنی؟"},
    {"key": "self_disclosure", "text": "به نظرات تو رازهای خودتو به این پسر/دختر میگی؟"},
]

ANSWER_OPTIONS = [
    "هیچکدوم",
    "فقط یه کوچولو",
    "نصفش",
    "بیشترش",
    "همه‌ش",
]

ANSWER_MAPPING = {text: idx + 1 for idx, text in enumerate(ANSWER_OPTIONS)}