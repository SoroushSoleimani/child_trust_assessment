from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from .participant import Participant
from .response import QuestionResponse

# ============================================================================
# SCENARIO RESPONSE DATA MODEL
# ============================================================================
# This module defines the data structures for storing all responses from a test
# session. It includes:
#   - ScenarioResponse: responses for a single scenario (8 total)
#   - TestSession: overall session containing participant info, scenario order,
#     and all scenario responses.

@dataclass
class ScenarioResponse:
    """
    Data class representing a participant's answers for ONE scenario.
    
    Each scenario contains 4 questions (niceness, trust, self_disclosure, correctness).
    This class aggregates the QuestionResponse objects for those questions.
    
    Attributes:
        scenario_name (str): Name of the scenario (e.g., "SEN1", "SEN2", ...).
        display_order (int): The order (1-8) in which this scenario was presented.
        responses (Dict[str, QuestionResponse]): Dictionary mapping question keys
            (e.g., "niceness") to their corresponding QuestionResponse objects.
    """
    
    scenario_name: str                                 # e.g., "SEN1"
    display_order: int                                 # 1-based order in the randomized sequence
    responses: Dict[str, QuestionResponse] = field(default_factory=dict)
    # ↑ responses[question_key] = QuestionResponse object
    
    def is_complete(self) -> bool:
        """
        Check if all 4 required questions have been answered for this scenario.
        
        Returns:
            bool: True if the responses dictionary contains keys for all required
                  question types; False otherwise.
        """
        required_keys = {"correctness", "niceness", "trust", "self_disclosure"}
        return required_keys.issubset(self.responses.keys())


@dataclass
class TestSession:
    """
    Data class representing a complete test session for one participant.
    
    Manages the participant's information, the randomized order of scenarios,
    all responses collected, and session timestamps.
    
    Attributes:
        participant (Participant): Participant object containing personal details.
        scenario_order (List[str]): Randomized list of 8 scenario names (e.g., ["SEN3", "SEN1", ...]).
        responses (List[ScenarioResponse]): List of ScenarioResponse objects, one per completed scenario.
        start_time (datetime): Timestamp when the session started (automatically set).
        end_time (Optional[datetime]): Timestamp when the session ended (set after finishing).
        current_scenario_index (int): Index of the scenario currently being presented (0-7).
    """
    
    participant: Participant
    scenario_order: List[str]
    responses: List[ScenarioResponse] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)   # Auto-set to current time
    end_time: Optional[datetime] = None
    current_scenario_index: int = 0
    
    def add_response(self, scenario_name: str, response: QuestionResponse):
        """
        Add a single question response to the appropriate scenario.
        
        If a ScenarioResponse for the given scenario_name already exists,
        it updates the responses dictionary with the new QuestionResponse.
        If no ScenarioResponse exists for that scenario, it creates a new one
        and appends it to the responses list.
        
        The display_order is derived from the scenario_order list (1-based index).
        
        Args:
            scenario_name (str): The name of the scenario (e.g., "SEN1").
            response (QuestionResponse): The response object containing question_key
                and answer_value.
        """
        # Search for an existing ScenarioResponse for this scenario
        for sr in self.responses:
            if sr.scenario_name == scenario_name:
                sr.responses[response.question_key] = response
                return
        
        # If not found, create a new ScenarioResponse
        # Compute display order: position in scenario_order + 1 (1-based)
        order = self.scenario_order.index(scenario_name) + 1 if scenario_name in self.scenario_order else len(self.responses) + 1
        new_sr = ScenarioResponse(
            scenario_name=scenario_name,
            display_order=order,
            responses={response.question_key: response}
        )
        self.responses.append(new_sr)
    
    def is_complete(self) -> bool:
        """
        Check if the entire test session is complete.
        
        A session is complete when:
            1. Exactly 8 scenarios have responses (len(responses) == 8).
            2. Each ScenarioResponse has all 4 required question responses.
        
        Returns:
            bool: True if all scenarios are fully answered; False otherwise.
        """
        if len(self.responses) != 8:
            return False
        # Verify each scenario response is complete (has all 4 question keys)
        return all(sr.is_complete() for sr in self.responses)