from dataclasses import dataclass
from typing import Optional

@dataclass
class QuestionResponse:
    question_key: str
    answer_value: int
    response_time_ms: Optional[int] = None