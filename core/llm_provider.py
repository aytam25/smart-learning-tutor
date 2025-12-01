import os
from typing import Optional

class LLMProvider:
    def complete(self, prompt: str, system: Optional=str, temperature: float=0.2) -> str:
        raise NotImplementedError

class DummyLLM(LLMProvider):
    def complete(self, prompt: str, system: Optional[str]=None, temperature: float=0.2) -> str:
        # مُولّد بسيط يقدّم شرحًا منظمًا بدون اتصال خارجي
        return (
            "شرح مبسّط:\n"
            "- تعريف المفهوم.\n"
            "- مثال واقعي قصير.\n"
            "- خطوة بخطوة لحل نموذج مشابه.\n"
            "نصيحة: إذا شعرت بصعوبة، ارجع للتعريف وجرّب مثالًا أسهل."
        )

def build_llm_provider() -> LLMProvider:
    provider = os.getenv("LLM_PROVIDER", "dummy").lower()
    if provider == "dummy":
        return DummyLLM()
    # يمكن إضافة مزودات حقيقية هنا (OpenAI، إلخ) عبر مفاتيح .env
    # حفاظًا على بساطة المشروع الجامعي، نتركها اختيارية.
    return DummyLLM()