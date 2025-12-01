from typing import List, Dict

class NLPUtils:
    @staticmethod
    def estimate_level(history: List[Dict]) -> str:
        # تقدير بسيط: إذا كانت الإجابات الصحيحة قليلة -> مبتدئ، أكثر -> متوسط، مرتفع -> متقدم
        attempts = sum(1 for h in history if h.get("type") == "exercise")
        corrects = sum(1 for h in history if h.get("type") == "exercise" and h.get("correct", False))
        if attempts < 3:
            return "beginner"
        ratio = corrects / max(1, attempts)
        if ratio < 0.4:
            return "beginner"
        elif ratio < 0.75:
            return "intermediate"
        else:
            return "advanced"

    @staticmethod
    def extract_concepts(text: str, available_concepts: List[str]) -> List[str]:
        # استخراج مبسّط: مطابقة كلمات المفهوم
        text_low = text.lower()
        hits = [c for c in available_concepts if c.lower() in text_low]
        return hits or available_concepts[:2]

    @staticmethod
    def structure_feedback(diff: Dict) -> Dict:
        # تحويل الفروقات إلى رسائل مهيكلة
        if diff.get("correct"):
            return {
                "score": diff.get("score", 1),
                "max_score": diff.get("max_score", 1),
                "feedback": "إجابة صحيحة! أحسنت. تابع إلى تمرين أصعب قليلًا.",
                "next_step": "جرّب تمرينًا على نفس المفهوم بمستوى أعلى."
            }
        else:
            hints = diff.get("hints", ["راجع التعريف الأساسي للمفهوم.", "قسّم المسألة إلى خطوات أبسط."])
            return {
                "score": diff.get("score", 0),
                "max_score": diff.get("max_score", 1),
                "feedback": "الإجابة غير دقيقة. " + " ".join(hints),
                "next_step": diff.get("next", "اقرأ مثالًا مشابهًا ثم أعد المحاولة.")
            }