from dataclasses import dataclass
from typing import Optional

# ============================================================================
# PARTICIPANT DATA MODEL
# ============================================================================
# This module defines the data structure for storing information about a
# child (participant) who takes the trust assessment test.
# Using a dataclass provides automatic __init__, __repr__, and other methods
# with minimal boilerplate code.

@dataclass
class Participant:
    """
    Data class representing a test participant (child).
    
    Attributes:
        code (int): Unique 4-digit random identifier assigned to each participant.
        name (str): Full name of the child.
        age (int): Age of the child in years.
        grade (str): School grade (e.g., "اول", "دوم" - Persian grade levels).
        gender (str): Either "girl" or "boy".
        session_date (Optional[str]): Date of the test session (YYYY-MM-DD format). Default None.
        session_time (Optional[str]): Time of the test session (HH:MM:SS format). Default None.
    """
    
    # ------------------------------------------------------------------------
    # Class fields (automatically become constructor parameters)
    # ------------------------------------------------------------------------
    code: int                       # Unique participant code (e.g., 1234)
    name: str                       # Participant's full name
    age: int                        # Participant's age
    grade: str                      # School grade in Persian text
    gender: str                     # Gender: "girl" or "boy"
    session_date: Optional[str] = None   # Test date (optional, set later)
    session_time: Optional[str] = None   # Test time (optional, set later)
    
    # ------------------------------------------------------------------------
    # INSTANCE METHODS
    # ------------------------------------------------------------------------
    
    def to_dict(self) -> dict:
        """
        Convert the Participant object into a dictionary suitable for saving
        to an Excel file or for logging.
        
        The dictionary keys are written in Persian to match the column headers
        expected by the Excel export functionality. Gender is converted from
        "girl"/"boy" to Persian strings ("دختر"/"پسر").
        
        Returns:
            dict: A dictionary with Persian keys and corresponding participant values.
        """
        return {
            "کد آزمودنی": self.code,                              # Participant code
            "نام و نام خانوادگی": self.name,                     # Full name
            "سن": self.age,                                      # Age
            "پایه تحصیلی": self.grade,                           # Grade level
            "جنسیت": "دختر" if self.gender == "girl" else "پسر", # Gender in Persian
            "تاریخ اجرا": self.session_date or "",               # Test date (empty if None)
            "ساعت اجرا": self.session_time or "",                # Test time (empty if None)
        }