import os
import json
from typing import Dict

class Persistence:
    def __init__(self, store_path: str = ".sessions"):
        self.store_path = store_path
        os.makedirs(store_path, exist_ok=True)

    def _fp(self, user_id: str) -> str:
        return os.path.join(self.store_path, f"{user_id}.json")

    def load_session(self, user_id: str) -> Dict:
        fp = self._fp(user_id)
        if not os.path.exists(fp):
            return {"history": [], "stats": {"correct": 0, "attempts": 0}, "level": "beginner"}
        with open(fp, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_session(self, user_id: str, session: Dict) -> None:
        fp = self._fp(user_id)
        with open(fp, "w", encoding="utf-8") as f:
            json.dump(session, f, ensure_ascii=False, indent=2)