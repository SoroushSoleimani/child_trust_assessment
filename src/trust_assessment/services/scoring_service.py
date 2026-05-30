import pandas as pd
from typing import Dict, List, Optional
from ..utils.config import SCORING_KEYS_FILE

class ScoringService:
    
    def __init__(self):
        self.scoring_keys = self._load_keys()
    
    def _load_keys(self) -> Dict:
        try:
            df = pd.read_excel(SCORING_KEYS_FILE, sheet_name=None)
            return df
        except:
            return {}
    
    def get_scores(self, scenario: str, question_type: str, answer_value: int) -> Dict:
        result = {
            "بي اعتمادي": 0,
            "اعتماد معرفتي": 0,
            "ساده لوحي": 0
        }
        
        if not self.scoring_keys:
            return result
        
        if "Sheet2" not in self.scoring_keys:
            return result
        
        df = self.scoring_keys["Sheet2"]
        
        if "سناریو" not in df.columns:
            return result
        
        mask = df["سناریو"] == scenario
        filtered = df[mask]
        
        if len(filtered) == 0:
            return result
        
        for _, row in filtered.iterrows():
            if row.get("شماره گزینه", 0) == answer_value:
                result["بي اعتمادي"] = int(row.get("بی اعتمادی", 0))
                result["اعتماد معرفتي"] = int(row.get("اعتماد", 0))
                result["ساده لوحي"] = int(row.get("ساده لوحی", 0))
                break
        
        return result
    
    def calculate_trust_score(self, responses: Dict) -> Dict:
        scores = {
            "بي اعتمادي": 0,
            "اعتماد معرفتي": 0,
            "ساده لوحي": 0
        }
        
        for scenario, answers in responses.items():
            for q_type, answer in answers.items():
                s = self.get_scores(scenario, q_type, answer)
                scores["بي اعتمادي"] += s["بي اعتمادي"]
                scores["اعتماد معرفتي"] += s["اعتماد معرفتي"]
                scores["ساده لوحي"] += s["ساده لوحي"]
        
        return scores