import json
import os
from typing import List, Dict

class KnowledgeBase:
    def __init__(self, data_path: str = "data"):
        self.data_path = data_path
        self.cache: Dict[str, dict] = {}
    
    def _load(self, subject: str) -> dict:
        if subject in self.cache:
            return self.cache[subject]
        fp = os.path.join(self.data_path, f"{subject}.json")
        with open(fp, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.cache[subject] = data
        return data

    def get_concepts(self, subject: str) -> List[str]:
        data = self._load(subject)
        return [c["name"] for c in data.get("concepts", [])]

    def get_examples(self, subject: str, concept: str) -> List[str]:
        data = self._load(subject)
        for c in data.get("concepts", []):
            if c["name"] == concept:
                return c.get("examples", [])
        return []

    def get_exercises(self, subject: str, concept: str, level: str) -> List[dict]:
        data = self._load(subject)
        pool = []
        for ex in data.get("exercises", []):
            if ex["concept"] == concept and ex["level"] == level:
                pool.append(ex)
        return pool