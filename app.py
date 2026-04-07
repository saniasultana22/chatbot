import streamlit as st
import requests
from datetime import datetime
import speech_recognition as sr
import pyttsx3
from reportlab.platypus import SimpleDocTemplate, Paragraph
from pptx import Presentation

# ------------------ PAGE SETUP ------------------
st.set_page_config(page_title="NLP Chatbot", page_icon="🤖")
st.title("🤖 NLP Chatbot (Advanced)")

api_key = st.secrets["OPENROUTER_API_KEY"]
model = "openai/gpt-4o-mini"

today = datetime.now().strftime("%A, %B %d, %Y")
SYSTEM_PROMPT = f"You are a helpful assistant. Today's date is {today}."

# ------------------ FUNCTIONS ------------------

# 🎤 Voice Input
def voice_input():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Speak now...")
        audio = r.listen(source)

    try:
        text = r.recognize_google(audio)
        return text
    except:
        return "Sorry, I couldn't understand"

# 🔊 Voice Output
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# 📄 Create PDF
def create_pdf(text):
    pdf = SimpleDocTemplate("chat_output.pdf")
    content = [Paragraph(text)]
    pdf.build(content)

# 📊 Create PPT
def create_ppt(text):
    prs = Presentation()
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Chatbot Response"
    slide.placeholders[1].text = text
    prs.save("chat_output.pptx")

# 🤖 Chatbot API Call
def get_response(messages):
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "https://your-app.streamlit.app",
                "X-Title": "NLP Chatbot",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": messages
            },
            timeout=30
        )

        data = response.json()

        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        elif "error" in data:
            return f"❌ {data['error']['message']}"
        else:
            return "❌ Unexpected response"

    except Exception as e:
        return f"❌ Error: {str(e)}"

# ------------------ SIDEBAR ------------------
with st.sidebar:
    st.header("⚙️ Settings")
    st.markdown(f"**Model:** `{model}`")
    st.caption(f"📅 {today}")

    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# ------------------ SESSION ------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ------------------ DISPLAY CHAT ------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ------------------ INPUT SECTION ------------------
user_input = None

col1, col2 = st.columns(2)

with col1:
    if st.button("🎙️ Speak"):
        user_input = voice_input()

with col2:
    text_input = st.chat_input("Type a message...")
    if text_input:
        user_input = text_input

# ------------------ PROCESS INPUT ------------------
if user_input:

    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):

            messages_with_system = [
                {"role": "system", "content": SYSTEM_PROMPT}
            ] + st.session_state.messages

            reply = get_response(messages_with_system)

            st.write(reply)

            # 🔊 Speak response
            speak(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})

    # ------------------ EXTRA FEATURES ------------------

    st.subheader("⬇️ Download Options")

    col3, col4 = st.columns(2)

    with col3:
        if st.button("📄 Download PDF"):
            create_pdf(reply)
            with open("chat_output.pdf", "rb") as f:
                st.download_button("Download PDF", f, file_name="chat.pdf")

    with col4:
        if st.button("📊 Download PPT"):
            create_ppt(reply)
            with open("chat_output.pptx", "rb") as f:
                st.download_button("Download PPT", f, file_name="chat.pptx")
