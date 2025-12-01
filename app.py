import streamlit as st
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import io

# اختيار اللغة
language = st.sidebar.selectbox("🌐 اختر اللغة", ["ar", "en"], index=0)

# ضبط اتجاه الصفحة
st.markdown(
    f"""<style>
    .reportview-container .main {{
        direction: {"rtl" if language == "ar" else "ltr"};
        text-align: {"right" if language == "ar" else "left"};
    }}
    </style>""",
    unsafe_allow_html=True
)

# تسجيل السؤال بالصوت
def record_and_transcribe():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙️ تحدث الآن...")
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio, language=language)
    except sr.UnknownValueError:
        return "لم يتم التعرف على الكلام"

# تحويل النص إلى صوت
def speak(text, lang="ar"):
    tts = gTTS(text, lang=lang)
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    st.audio(mp3_fp.getvalue(), format="audio/mp3")

# واجهة السؤال الصوتي
st.subheader("🎤 اسأل بالصوت")
if st.button("🎙️ تسجيل السؤال"):
    question = record_and_transcribe()
    st.text_area("📄 السؤال المكتوب:", value=question, height=100)

# مثال تشغيل صوت الإجابة
if st.button("🔊 تشغيل إجابة تجريبية"):
    speak("مرحبًا بك في نظام التعلم الذكي", lang=language)