
import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="NLP Chatbot", page_icon="🤖")
st.title("🤖 NLP Chatbot")

api_key = st.secrets["OPENROUTER_API_KEY"]
model = "openai/gpt-4o-mini"

# System prompt with today's real date injected
today = datetime.now().strftime("%A, %B %d, %Y")
SYSTEM_PROMPT = f"You are a helpful assistant. Today's date is {today}. Always use this date when answering any date or time related questions."

with st.sidebar:
    st.header("Settings")
    st.markdown(f"**Model:** `{model}`")
    st.caption(f"📅 Today: {today}")
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_input = st.chat_input("Type a message...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Prepend system message with today's date on every request
                messages_with_system = [
                    {"role": "system", "content": SYSTEM_PROMPT}
                ] + st.session_state.messages

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
                        "messages": messages_with_system
                    },
                    timeout=30
                )
                data = response.json()
                if "choices" in data:
                    reply = data["choices"][0]["message"]["content"]
                elif "error" in data:
                    reply = f"❌ Error {data['error'].get('code', '')}: {data['error'].get('message', 'Unknown error')}"
                else:
                    reply = f"❌ Unexpected response: {data}"
            except requests.exceptions.Timeout:
                reply = "❌ Request timed out. Please try again."
            except Exception as e:
                reply = f"❌ Error: {str(e)}"
        st.write(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
