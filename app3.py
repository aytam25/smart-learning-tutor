import streamlit as st
import json
import os
import random
from core.tutor_agent import TutorAgent
from core.knowledge_base import KnowledgeBase
from core.persistence import Persistence
from core.llm_provider import build_llm_provider

# إعداد الواجهة
st.set_page_config(page_title="نظام تعليمي ذكي", page_icon="🎓", layout="wide")
st.title("🎓 نظام تعليمي ذكي — Smart Learning Tutor")
st.caption("يوظف NLP لتخصيص الشرح، وتصحيح الأخطاء خطوة بخطوة، وتمارين مناسبة للمستوى.")

# دالة لتحميل بيانات الدرس
def load_lesson(subject):
    path = os.path.join("data", f"{subject}.json")
    if not os.path.exists(path):
        st.error(f"⚠️ الملف {subject}.json غير موجود.")
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# اختيار اسم الدرس من الشريط الجانبي
subject = st.sidebar.selectbox("📘 اختر اسم الدرس", [
    "math_basics",
    "python_basics",
    "english_basics",
    "logic_basics"
])

# زر لتحديث التمارين
if st.sidebar.button("🔄 تحديث التمارين"):
    st.session_state["lesson"] = load_lesson(subject)
    st.success(f"✅ تم تحديث التمارين من الملف: {subject}.json")

# تحميل الدرس عند التشغيل
if "lesson" not in st.session_state:
    st.session_state["lesson"] = load_lesson(subject)

lesson = st.session_state["lesson"]

# إعداد الوكلاء
kb = KnowledgeBase(data_path="data")
persistence = Persistence(store_path=".sessions")
llm = build_llm_provider()
agent = TutorAgent(kb=kb, llm=llm, persistence=persistence)

# قسم الأسئلة
st.subheader("❓ اسأل عن المفاهيم")
question = st.text_area("✍️ اكتب سؤالك هنا…", height=120, placeholder="مثال: ما هو المتغير؟ أو كيف أجمع الكسور؟")
if st.button("إجابة مخصصة"):
    if question.strip():
        res = agent.handle_question(user_id="guest", subject=subject, text=question)
        st.markdown("**📖 الشرح المخصص:**")
        st.write(res.get("explanation"))
        st.markdown("**🔗 المفاهيم ذات الصلة:** " + ", ".join(res.get("concepts", [])))
        st.markdown("**🎯 المستوى التقديري:** " + res.get("estimated_level", "unknown"))
    else:
        st.warning("⚠️ الرجاء كتابة السؤال.")

st.divider()

# قسم التمارين
st.subheader("🧩 تمارين تفاعلية")

if lesson:
    # عرض صورة رمزية للدرس إذا توفرت
    if "image" in lesson:
        st.image(f"docs/images/{lesson['image']}", width=150)

    # اختيار المفهوم
    concept_names = [c["name"] for c in lesson["concepts"]]
    selected_concept = st.selectbox("اختر مفهومًا", concept_names)

    # عرض وصف المفهوم
    concept_info = next((c for c in lesson["concepts"] if c["name"] == selected_concept), None)
    if concept_info:
        st.markdown(f"**📖 وصف المفهوم:** {concept_info['description']}")
        if "examples" in concept_info:
            st.markdown("**🧪 أمثلة:**")
            for ex in concept_info["examples"]:
                st.code(ex)

    # اختيار مستوى الصعوبة
    selected_level = st.radio("🎯 اختر المستوى", ["beginner", "intermediate", "advanced"])

    # زر بدء أو إعادة تعيين التمرين
    if st.button("ولّد تمرين") or st.button("🔁 إعادة تعيين التمرين"):
        ex = agent.generate_exercise(subject=subject, concept=selected_concept, level=selected_level)
        st.session_state.current_exercise = ex
        st.markdown("**🧠 نص التمرين:**")
        st.write(ex["prompt"])
        if "hint" in ex:
            if st.button("💡 عرض تلميح"):
                st.info(f"💡 التلميح: {ex['hint']}")

    # إدخال الإجابة
    user_answer = st.text_input("✍️ إجابتك")
    if st.button("تصحيح الإجابة"):
        ex = st.session_state.get("current_exercise")
        if not ex:
            st.warning("⚠️ الرجاء توليد تمرين أولاً.")
        else:
            graded = agent.grade_answer(exercise=ex, user_answer=user_answer, user_id="guest")
            st.markdown(f"**📊 النتيجة:** {graded['score']} / {graded['max_score']}")
            st.markdown("**🔎 تغذية راجعة:**")
            st.write(graded["feedback"])
            if graded.get("next_step"):
                st.markdown("**➡️ الخطوة التالية المقترحة:**")
                st.write(graded["next_step"])