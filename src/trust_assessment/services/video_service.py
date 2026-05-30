import os
import random
from typing import List, Optional
from ..utils.config import GIRLS_VIDEOS_DIR, BOYS_VIDEOS_DIR, VIDEO_EXTENSIONS, SENARIO_NAMES

class VideoService:
    
    def __init__(self, gender: str):
        self.gender = gender
        if gender == "girl":
            self.video_dir = GIRLS_VIDEOS_DIR
        else:
            self.video_dir = BOYS_VIDEOS_DIR
    
    def get_available_videos(self) -> List[str]:
        videos = []
        for filename in os.listdir(self.video_dir):
            name_without_ext = os.path.splitext(filename)[0]
            if name_without_ext in SENARIO_NAMES:
                videos.append(name_without_ext)
        return videos
    
    def get_video_path(self, scenario_name: str) -> Optional[str]:
        for ext in VIDEO_EXTENSIONS:
            path = os.path.join(self.video_dir, f"{scenario_name}{ext}")
            if os.path.exists(path):
                return path
        folder_path = os.path.join(self.video_dir, scenario_name)
        if os.path.exists(folder_path):
            for ext in VIDEO_EXTENSIONS:
                path = f"{folder_path}{ext}"
                if os.path.exists(path):
                    return path
        for filename in os.listdir(self.video_dir):
            name_without_ext = os.path.splitext(filename)[0]
            if name_without_ext == scenario_name:
                return os.path.join(self.video_dir, filename)
        return None
    
    def get_random_order(self) -> List[str]:
        available = self.get_available_videos()
        if len(available) == 8:
            shuffled = available.copy()
            random.shuffle(shuffled)
            return shuffled
        else:
            found = []
            for name in SENARIO_NAMES:
                if self.get_video_path(name) is not None:
                    found.append(name)
            if len(found) == 8:
                random.shuffle(found)
                return found
        return SENARIO_NAMES.copy()
    
    def check_videos_exist(self) -> bool:
        found_count = 0
        for name in SENARIO_NAMES:
            if self.get_video_path(name) is not None:
                found_count += 1
        return found_count == 8