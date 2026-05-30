from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from .participant import Participant
from .response import QuestionResponse

@dataclass
class ScenarioResponse:
    scenario_name: str
    display_order: int
    responses: Dict[str, QuestionResponse] = field(default_factory=dict)
    
    def is_complete(self) -> bool:
        required_keys = {"correctness", "niceness", "trust", "self_disclosure"}
        return required_keys.issubset(self.responses.keys())

@dataclass
class TestSession:
    participant: Participant
    scenario_order: List[str]
    responses: List[ScenarioResponse] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    current_scenario_index: int = 0
    
    def add_response(self, scenario_name: str, response: QuestionResponse):
        for sr in self.responses:
            if sr.scenario_name == scenario_name:
                sr.responses[response.question_key] = response
                return
        
        order = self.scenario_order.index(scenario_name) + 1 if scenario_name in self.scenario_order else len(self.responses) + 1
        new_sr = ScenarioResponse(
            scenario_name=scenario_name,
            display_order=order,
            responses={response.question_key: response}
        )
        self.responses.append(new_sr)
    
    def is_complete(self) -> bool:
        if len(self.responses) != 8:
            return False
        return all(sr.is_complete() for sr in self.responses)