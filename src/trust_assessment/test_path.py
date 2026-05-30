import os

print("=== تست مسیرها ===\n")

current_file = os.path.abspath(__file__)
print("مسیر فایل فعلی:", current_file)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
print("ROOT_DIR محاسبه شده:", ROOT_DIR)

VIDEOS_DIR = os.path.join(ROOT_DIR, "src", "trust_assessment", "assets", "videos")
print("VIDEOS_DIR:", VIDEOS_DIR)

GIRLS_DIR = os.path.join(VIDEOS_DIR, "girls")
print("GIRLS_DIR:", GIRLS_DIR)
print("آیا وجود دارد؟", os.path.exists(GIRLS_DIR))

BOYS_DIR = os.path.join(VIDEOS_DIR, "boys")
print("BOYS_DIR:", BOYS_DIR)
print("آیا وجود دارد؟", os.path.exists(BOYS_DIR))

print("\n=== لیست فایل‌های boys ===")
if os.path.exists(BOYS_DIR):
    for f in os.listdir(BOYS_DIR):
        print(f)
else:
    print("پوشه وجود ندارد!")