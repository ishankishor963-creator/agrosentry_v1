import streamlit as st

from utils.ai_agent import ai_reply
from utils.theme import inject_theme, topnav
from utils.auth import logout_button


# ------------------------------------------------------------
# PAGE SETUP
# ------------------------------------------------------------

inject_theme()

with st.sidebar:
    logout_button()

topnav("ai")


# ------------------------------------------------------------
# HEADER
# ------------------------------------------------------------

st.title("🤖 AI Farming Assistant")

st.caption(
    "Ask questions about your crops, irrigation, soil, "
    "weather, pests and plant health."
)


# ------------------------------------------------------------
# CHAT HISTORY
# ------------------------------------------------------------

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []


# ------------------------------------------------------------
# DISPLAY PREVIOUS MESSAGES
# ------------------------------------------------------------

for message in st.session_state["chat_history"]:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ------------------------------------------------------------
# QUICK QUESTIONS
# ------------------------------------------------------------

st.markdown("### Quick questions")

col1, col2, col3 = st.columns(3)

quick_question = None

with col1:
    if st.button(
        "💧 Should I irrigate?",
        use_container_width=True,
    ):
        quick_question = "Should I irrigate my field?"

with col2:
    if st.button(
        "🍃 Why are leaves yellow?",
        use_container_width=True,
    ):
        quick_question = "Why are my crop leaves turning yellow?"

with col3:
    if st.button(
        "🐛 Pest problem",
        use_container_width=True,
    ):
        quick_question = "What should I do about pests?"


# ------------------------------------------------------------
# CHAT INPUT
# ------------------------------------------------------------

question = st.chat_input(
    "Ask about your farm..."
)


# Quick question takes priority
if quick_question:
    question = quick_question


# ------------------------------------------------------------
# PROCESS MESSAGE
# ------------------------------------------------------------

if question:

    # User message
    st.session_state["chat_history"].append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    # Previous history excluding current user message
    history = st.session_state["chat_history"][:-1]

    # AI response
    answer = ai_reply(
        question,
        history=history,
    )

    # Save response
    st.session_state["chat_history"].append(
        {
            "role": "assistant",
            "content": answer,
        }
    )

    with st.chat_message("assistant"):
        st.markdown(answer)


# ------------------------------------------------------------
# CLEAR CHAT
# ------------------------------------------------------------

if st.session_state["chat_history"]:

    st.divider()

    if st.button(
        "🗑️ Clear conversation",
        use_container_width=False,
    ):

        st.session_state["chat_history"] = []

        st.rerun()
