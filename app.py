import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# -----------------------------
# 1. Load environment variables
# -----------------------------
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("OPENAI_API_KEY not found. Please check your .env file.")
    st.stop()

client = OpenAI(api_key=api_key)

# -----------------------------
# 2. Load default knowledge base
# -----------------------------
def load_knowledge_base():
    with open("knowledge_base.txt", "r") as file:
        return file.read()

if "knowledge_base" not in st.session_state:
    st.session_state.knowledge_base = load_knowledge_base()

# -----------------------------
# 3. Page setup
# -----------------------------
st.set_page_config(
    page_title="AI Support Chatbot",
    page_icon="💬",
    layout="centered"
)

# -----------------------------
# 4. Sidebar
# -----------------------------
with st.sidebar:
    st.title("⚙️ Settings")

    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")

    uploaded_file = st.file_uploader(
        "📄 Upload support document (.txt)",
        type=["txt"]
    )

    if uploaded_file:
        st.session_state.knowledge_base = uploaded_file.read().decode("utf-8")
        st.success("Document uploaded successfully!")

    st.markdown("---")
    st.write("💡 Example Questions:")
    st.write("- What is your refund policy?")
    st.write("- What plans do you offer?")
    st.write("- When is support available?")

# -----------------------------
# 5. Main UI
# -----------------------------
st.title("E-commerce Support Chatbot")
st.caption("AI-powered assistant for customer support")

# -----------------------------
# 6. Chat memory
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# -----------------------------
# 7. User input
# -----------------------------
user_question = st.chat_input("Ask a support question...")

if user_question:
    st.session_state.messages.append({
        "role": "user",
        "content": user_question
    })

    with st.chat_message("user"):
        st.write(user_question)

    system_prompt = f"""
    You are a professional customer support assistant.

    Rules:
    - Answer ONLY from the provided knowledge base.
    - Do NOT make up answers.
    - If the answer is not found, say:
      "I'm sorry, I don't have that information in the current support documents."

    Knowledge Base:
    {st.session_state.knowledge_base}
    """

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        assistant_reply = ""

        stream = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                *st.session_state.messages
            ],
            stream=True
        )

        for chunk in stream:
            try:
                content = chunk.choices[0].delta.content
                if content:
                    assistant_reply += content
                    message_placeholder.write(assistant_reply)
            except:
                pass

    st.session_state.messages.append({
        "role": "assistant",
        "content": assistant_reply
    })
# -----------------------------
# 10. Download chat history (NEW)
# -----------------------------
if st.session_state.messages:
    chat_text = ""

    for msg in st.session_state.messages:
        role = "User" if msg["role"] == "user" else "Assistant"
        chat_text += f"{role}: {msg['content']}\n\n"

    st.download_button(
        label="⬇️ Download Chat History",
        data=chat_text,
        file_name="chat_history.txt",
        mime="text/plain"
    )
