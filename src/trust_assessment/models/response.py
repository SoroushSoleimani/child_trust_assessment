from dataclasses import dataclass
from typing import Optional

# ============================================================================
# QUESTION RESPONSE DATA MODEL
# ============================================================================
# This module defines the data structure for storing a child's answer to a
# single question within a specific scenario. Each response is associated with
# a particular question type (e.g., niceness, trust, self-disclosure, correctness)
# and contains the selected answer value along with an optional response time.

@dataclass
class QuestionResponse:
    """
    Data class representing a participant's response to one question.
    
    For each of the 4 questions per scenario (niceness, trust, self_disclosure,
    correctness), the child selects one of 5 answer options (1 to 5). This class
    captures that selection along with timing metadata for analysis.
    
    Attributes:
        question_key (str): Identifier for the question type.
            Expected values: "niceness", "trust", "self_disclosure", "correctness".
        answer_value (int): The child's selected answer on a 1-5 scale.
            1 = lowest agreement/trust, 5 = highest agreement/trust.
        response_time_ms (Optional[int]): Time taken to answer the question,
            measured in milliseconds. Can be None if not recorded or not needed.
    """
    
    # ------------------------------------------------------------------------
    # CLASS FIELDS (automatically become constructor parameters)
    # ------------------------------------------------------------------------
    question_key: str                     # Which question was asked (e.g., "niceness")
    answer_value: int                     # Selected option value (1 through 5)
    response_time_ms: Optional[int] = None   # Time spent on this question (milliseconds)