import random
from typing import Dict, Any
from .schemas import Exercise, GradeResult, QAResult
from .nlp_utils import NLPUtils
from .llm_provider import LLMProvider
from .knowledge_base import KnowledgeBase
from .persistence import Persistence

class TutorAgent:
    def __init__(self, kb: KnowledgeBase, llm: LLMProvider, persistence: Persistence):
        self.kb = kb
        self.llm = llm
        self.persistence = persistence

    def _session(self, user_id: str) -> Dict[str, Any]:
        return self.persistence.load_session(user_id)

    def _save(self, user_id: str, session: Dict[str, Any]) -> None:
        self.persistence.save_session(user_id, session)

    def get_progress_summary(self, user_id: str) -> str:
        s = self._session(user_id)
        attempts = s["stats"]["attempts"]
        corrects = s["stats"]["correct"]
        level = NLPUtils.estimate_level(s["history"])
        return f"المحاولات: {attempts}, الصحيحة: {corrects}, المستوى التقديري: {level}"

    def handle_question(self, user_id: str, subject: str, text: str) -> Dict:
        session = self._session(user_id)
        concepts = self.kb.get_concepts(subject)
        related = NLPUtils.extract_concepts(text, concepts)
        level = NLPUtils.estimate_level(session["history"])

        system = "أنت معلّم لطيف يشرح بحسب مستوى الطالب ويعطي أمثلة قصيرة وخطوات واضحة."
        prompt = (
            f"السؤال: {text}\n"
            f"المفاهيم ذات الصلة: {', '.join(related)}\n"
            f"مستوى الطالب: {level}\n"
            "اكتب شرحًا واضحًا ومخصصًا، مثالًا واحدًا، وخطوات تطبيق مختصرة."
        )
        explanation = self.llm.complete(prompt=prompt, system=system, temperature=0.2)
        session["history"].append({"type": "qa", "text": text, "related": related, "level": level})
        session["level"] = level
        self._save(user_id, session)
        return QAResult(explanation=explanation, concepts=related, estimated_level=level).dict()

    def generate_exercise(self, subject: str, concept: str, level: str) -> Dict:
        pool = self.kb.get_exercises(subject, concept, level)
        if not pool:
            # إذا لا يوجد تمارين، نصنع تمرينًا بسيطًا من أمثلة المفاهيم
            examples = self.kb.get_examples(subject, concept)
            prompt = f"اشرح المثال التالي ثم طبّقه: {examples[0] if examples else 'مثال بسيط'}"
            ex = Exercise(subject=subject, concept=concept, level=level, prompt=prompt, answer="(إجابة متوقعة)", meta={"generated": True})
            return ex.dict()
        chosen = random.choice(pool)
        ex = Exercise(subject=subject, concept=concept, level=level, prompt=chosen["prompt"], answer=chosen["answer"], meta={"generated": False})
        return ex.dict()

    def grade_answer(self, exercise: Dict, user_answer: str, user_id: str) -> Dict:
        # تصحيح مبسّط: مطابقة سلاسل/أرقام مع تحمل بسيط للأخطاء
        expected = exercise["answer"].strip().lower()
        ua = (user_answer or "").strip().lower()
        correct = expected == ua if expected and ua else False
        score = 1 if correct else 0
        diff = {
            "correct": correct,
            "score": score,
            "max_score": 1,
            "hints": [
                "قارن إجابتك بالخطوات المعروضة في الشرح.",
                "تحقق من التعريف، ثم أعد صياغة الحل خطوة خطوة."
            ],
            "next": "راجع مثالًا مشابهًا ثم أعد محاولة على مستوى أدنى إذا لزم."
        }

        # بناء تغذية راجعة مُعزّزة عبر الـ LLM (اختياري)
        system = "أنت مصحّح لطيف يعطي خطوات تصحيح بناءة دون إحباط."
        prompt = (
            f"التمرين: {exercise['prompt']}\n"
            f"الإجابة المتوقعة: {exercise['answer']}\n"
            f"إجابة الطالب: {user_answer}\n"
            "أعطِ تغذية راجعة قصيرة بثلاث نقاط: أين الخطأ/الصواب، خطوة تصحيح، ونصيحة متابعة."
        )
        llm_feedback = self.llm.complete(prompt=prompt, system=system, temperature=0.3)

        fb = NLPUtils.structure_feedback(diff)
        # دمج المخرجات: نضيف نص الـ LLM داخل التغذية الراجعة
        feedback = fb["feedback"] + "\n\n" + "توجيه إضافي:\n" + llm_feedback

        # تحديث الجلسة
        session = self._session(user_id)
        session["stats"]["attempts"] += 1
        if correct:
            session["stats"]["correct"] += 1
        session["history"].append({"type": "exercise", "concept": exercise["concept"], "level": exercise["level"], "correct": correct})
        self._save(user_id, session)

        return {
            "score": fb["score"],
            "max_score": fb["max_score"],
            "feedback": feedback,
            "next_step": fb["next_step"]
        }