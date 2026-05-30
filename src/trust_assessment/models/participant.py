from dataclasses import dataclass
from typing import Optional

@dataclass
class Participant:
    code: int
    name: str
    age: int
    grade: str
    gender: str
    session_date: Optional[str] = None
    session_time: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "کد آزمودنی": self.code,
            "نام و نام خانوادگی": self.name,
            "سن": self.age,
            "پایه تحصیلی": self.grade,
            "جنسیت": "دختر" if self.gender == "girl" else "پسر",
            "تاریخ اجرا": self.session_date or "",
            "ساعت اجرا": self.session_time or "",
        }