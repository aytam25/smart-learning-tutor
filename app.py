import streamlit as st
from core.tutor_agent import TutorAgent
from core.knowledge_base import KnowledgeBase
from core.persistence import Persistence
from core.llm_provider import build_llm_provider
import json
import os

def load_exercises(subject):
    path = os.path.join("data", f"{subject}.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# زر التحديث
if st.sidebar.button("🔄 تحديث التمارين"):
    data = load_exercises(subject)
    st.success(f"تم تحديث التمارين من الملف: {subject}.json")

# تحميل التمارين تلقائيًا عند التشغيل
data = load_exercises(subject)
st.set_page_config(page_title="Smart Learning Tutor", page_icon="🎓", layout="wide")

# حالة الجلسة
if "user_id" not in st.session_state:
    st.session_state.user_id = "guest"
if "subject" not in st.session_state:
    st.session_state.subject = "math_basics"

kb = KnowledgeBase(data_path="data")
persistence = Persistence(store_path=".sessions")
llm = build_llm_provider()
agent = TutorAgent(kb=kb, llm=llm, persistence=persistence)

st.title("🎓 نظام تعليمي ذكي — Smart Learning Tutor")
st.caption("يوظف NLP لتخصيص الشرح، وتصحيح الأخطاء خطوة بخطوة، وتمارين مناسبة للمستوى.")

# الشريط الجانبي
with st.sidebar:
   # واجهة اختيار الدرس
    subject = st.sidebar.selectbox("اختر اسم الدرس", ["math_basics", "python_basics", "english_basics", "logic_basics"])
    st.header("خيارات")
    subject = st.selectbox("اختر المادة", ["math_basics"], index=0)      
    st.session_state.subject = subject
    st.write("مستوى تقديري سيُحدّد تلقائيًا من الحوار.")
    if st.button("ملخص التقدم"):
        summary = agent.get_progress_summary(st.session_state.user_id)
        st.info(summary)

# قسم الأسئلة
st.subheader("اسأل عن المفاهيم")
question = st.text_area("اكتب سؤالك هنا…", height=120, placeholder="مثال: ما هو المتغير؟ أو كيف أجمع الكسور؟")
if st.button("إجابة مخصصة"):
    if question.strip():
        res = agent.handle_question(user_id=st.session_state.user_id, subject=st.session_state.subject, text=question)
        st.markdown("**الشرح المخصص:**")
        st.write(res.get("explanation"))
        st.markdown("**المفاهيم ذات الصلة:** " + ", ".join(res.get("concepts", [])))
        st.markdown("**مستوى تقديري:** " + res.get("estimated_level", "unknown"))
    else:
        st.warning("الرجاء كتابة السؤال.")

st.divider()

# قسم التمارين
st.subheader("تمارين تفاعلية")
concepts = kb.get_concepts(st.session_state.subject)
concept = st.selectbox("اختر مفهومًا", concepts)
level = st.select_slider("اختر المستوى", options=["beginner", "intermediate", "advanced"], value="beginner")

if st.button("ولّد تمرين"):
    ex = agent.generate_exercise(subject=st.session_state.subject, concept=concept, level=level)
    st.session_state.current_exercise = ex
    st.markdown("**نص التمرين:**")
    st.write(ex["prompt"])
    st.caption("أدخل إجابتك ثم اضغط تصحيح.")

user_answer = st.text_input("إجابتك")
if st.button("تصحيح الإجابة"):
    ex = st.session_state.get("current_exercise")
    if not ex:
        st.warning("الرجاء توليد تمرين أولاً.")
    else:
        graded = agent.grade_answer(exercise=ex, user_answer=user_answer, user_id=st.session_state.user_id)
        st.markdown(f"**النتيجة:** {graded['score']} / {graded['max_score']}")
        st.markdown("**تغذية راجعة:**")
        st.write(graded["feedback"])
        if graded.get("next_step"):
            st.markdown("**الخطوة التالية المقترحة:**")
            st.write(graded["next_step"])