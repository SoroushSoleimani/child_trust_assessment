import os
import pandas as pd
from datetime import datetime
from typing import List, Dict
from ..models.participant import Participant
from ..models.session import TestSession, ScenarioResponse
from ..utils.config import DATA_DIR, SCORING_KEYS_FILE

class ExcelService:
    
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
    
    def save_session(self, session: TestSession) -> str:
        filename = SCORING_KEYS_FILE
        
        if os.path.exists(filename):
            existing_data = pd.read_excel(filename, sheet_name=None)
        else:
            existing_data = {}
        
        sheet1_data = self._create_sheet1_data(session)
        sheet2_data = self._get_sheet2_data(existing_data)
        sheet3_data = self._create_sheet3_data(session, existing_data)
        
        with pd.ExcelWriter(filename, engine='openpyxl', mode='w') as writer:
            sheet1_data.to_excel(writer, sheet_name='Sheet1', index=False)
            sheet2_data.to_excel(writer, sheet_name='Sheet2', index=False)
            sheet3_data.to_excel(writer, sheet_name='Sheet3', index=False)
        
        return filename
    
    def _create_sheet1_data(self, session: TestSession) -> pd.DataFrame:
        sorted_responses = sorted(session.responses, key=lambda x: x.display_order)
        
        order_str = ''.join([r.scenario_name.replace('SEN', '') for r in sorted_responses])
        
        row = {
            "ردیف": session.participant.code,
            "نام": session.participant.name,
            "سن": session.participant.age,
            "کلاس": session.participant.grade,
            "نمایش اول": sorted_responses[0].scenario_name if len(sorted_responses) > 0 else "",
            "نمایش دوم": sorted_responses[1].scenario_name if len(sorted_responses) > 1 else "",
            "نمایش سوم": sorted_responses[2].scenario_name if len(sorted_responses) > 2 else "",
            "نمایش چهارم": sorted_responses[3].scenario_name if len(sorted_responses) > 3 else "",
            "نمایش پنجم": sorted_responses[4].scenario_name if len(sorted_responses) > 4 else "",
            "نمایش ششم": sorted_responses[5].scenario_name if len(sorted_responses) > 5 else "",
            "نمایش هفتم": sorted_responses[6].scenario_name if len(sorted_responses) > 6 else "",
            "نمایش هشتم": sorted_responses[7].scenario_name if len(sorted_responses) > 7 else "",
        }
        
        for sr in sorted_responses:
            col_nic = f"{sr.scenario_name}-NIC"
            col_t = f"{sr.scenario_name}-T"
            col_sd = f"{sr.scenario_name}-SD"
            col_co = f"{sr.scenario_name}-CO"
            
            if "niceness" in sr.responses:
                row[col_nic] = sr.responses["niceness"].answer_value
            if "trust" in sr.responses:
                row[col_t] = sr.responses["trust"].answer_value
            if "self_disclosure" in sr.responses:
                row[col_sd] = sr.responses["self_disclosure"].answer_value
            if "correctness" in sr.responses:
                row[col_co] = sr.responses["correctness"].answer_value
        
        return pd.DataFrame([row])
    
    def _get_sheet2_data(self, existing_data: Dict) -> pd.DataFrame:
        if 'Sheet2' in existing_data:
            return existing_data['Sheet2']
        
        default_data = {
            "سناریو": [],
            "شماره گزینه": [],
            "بی اعتمادی": [],
            "اعتماد": [],
            "ساده لوحی": []
        }
        
        for i in range(1, 9):
            for opt in range(1, 6):
                default_data["سناریو"].append(f"SEN{i}")
                default_data["شماره گزینه"].append(opt)
                default_data["بی اعتمادی"].append(0)
                default_data["اعتماد"].append(0)
                default_data["ساده لوحی"].append(0)
        
        return pd.DataFrame(default_data)
    
    def _create_sheet3_data(self, session: TestSession, existing_data: Dict) -> pd.DataFrame:
        scores = self._calculate_all_scores(session)
        
        sorted_responses = sorted(session.responses, key=lambda x: x.display_order)
        order_str = ''.join([r.scenario_name.replace('SEN', '') for r in sorted_responses])
        
        row = {
            "ردیف": session.participant.code,
            "نام": session.participant.name,
            "سن": session.participant.age,
            "کلاس": session.participant.grade,
            "ترتیب نمایش‌ها": order_str,
            "بی‌اعتمادی(خوب بودن)": scores["niceness"]["mistrust"],
            "اعتمادمعرفتی(خوب بودن)": scores["niceness"]["trust"],
            "ساده لوحی(خوب بودن)": scores["niceness"]["gullibility"],
            "بی‌اعتمادی(اعتماد)": scores["trust"]["mistrust"],
            "اعتمادمعرفتی(اعتماد)": scores["trust"]["trust"],
            "ساده لوحی(اعتماد)": scores["trust"]["gullibility"],
            "بی‌اعتمادی(خودافشایی)": scores["self_disclosure"]["mistrust"],
            "اعتمادمعرفتی(خودافشایی)": scores["self_disclosure"]["trust"],
            "ساده لوحی(خودافشایی)": scores["self_disclosure"]["gullibility"],
            "بی‌اعتمادی(درست بودن)": scores["correctness"]["mistrust"],
            "اعتمادمعرفتی(درست بودن)": scores["correctness"]["trust"],
            "ساده لوحی(درست بودن)": scores["correctness"]["gullibility"],
            "جمع بی اعتمادی": scores["total"]["mistrust"],
            "جمع اعتماد معرفتی": scores["total"]["trust"],
            "جمع ساده لوحی": scores["total"]["gullibility"]
        }
        
        return pd.DataFrame([row])
    
    def _calculate_all_scores(self, session: TestSession) -> Dict:
        scores = {
            "niceness": {"mistrust": 0, "trust": 0, "gullibility": 0},
            "trust": {"mistrust": 0, "trust": 0, "gullibility": 0},
            "self_disclosure": {"mistrust": 0, "trust": 0, "gullibility": 0},
            "correctness": {"mistrust": 0, "trust": 0, "gullibility": 0},
            "total": {"mistrust": 0, "trust": 0, "gullibility": 0}
        }
        
        for sr in session.responses:
            scenario = sr.scenario_name
            
            for q_type in ["niceness", "trust", "self_disclosure", "correctness"]:
                if q_type in sr.responses:
                    answer = sr.responses[q_type].answer_value
                    q_scores = self._get_score_from_keys(scenario, answer)
                    
                    scores[q_type]["mistrust"] += q_scores["mistrust"]
                    scores[q_type]["trust"] += q_scores["trust"]
                    scores[q_type]["gullibility"] += q_scores["gullibility"]
                    
                    scores["total"]["mistrust"] += q_scores["mistrust"]
                    scores["total"]["trust"] += q_scores["trust"]
                    scores["total"]["gullibility"] += q_scores["gullibility"]
        
        return scores
    
    def _get_score_from_keys(self, scenario: str, answer: int) -> Dict:
        if not os.path.exists(SCORING_KEYS_FILE):
            return {"mistrust": 0, "trust": 0, "gullibility": 0}
        
        try:
            df = pd.read_excel(SCORING_KEYS_FILE, sheet_name='Sheet2')
            mask = (df["سناریو"] == scenario) & (df["شماره گزینه"] == answer)
            filtered = df[mask]
            
            if len(filtered) > 0:
                row = filtered.iloc[0]
                return {
                    "mistrust": int(row.get("بی اعتمادی", 0)),
                    "trust": int(row.get("اعتماد", 0)),
                    "gullibility": int(row.get("ساده لوحی", 0))
                }
        except:
            pass
        
        return {"mistrust": 0, "trust": 0, "gullibility": 0}