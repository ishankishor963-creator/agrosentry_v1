"""
AgroSentry - AI Farm Assistant

Local sensor-based farm intelligence.

No external AI API is used.
"""

import streamlit as st

from utils.ai_agent import ai_reply
from utils.theme import inject_theme

# Existing AgroSentry navigation/auth components.
from utils.auth import logout_button

try:
    from utils.theme import topnav
except ImportError:
    topnav = None


# ---------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------

st.set_page_config(
    page_title="AI Farm Assistant | AgroSentry",
    page_icon="🤖",
    layout="wide",
)

inject_theme()


# ---------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------

try:
    logout_button()
except Exception:
    pass

if topnav is not None:
    try:
        topnav("ai")
    except Exception:
        pass


# ---------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------

st.title("🤖 AI Farm Assistant")

st.caption(
    "Local farm intelligence powered by your AgroSentry sensor data."
)

st.info(
    "This assistant does not use ChatGPT, Claude, or any external AI API. "
    "Its recommendations are generated from the latest available farm sensor readings."
)


# ---------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []


# ---------------------------------------------------------------------
# Suggested questions
# ---------------------------------------------------------------------

st.markdown("### Ask about your farm")

suggestions = [
    "How is my farm?",
    "Do I need irrigation?",
    "What is my soil moisture?",
    "What is the temperature?",
    "What is the humidity?",
    "What should I do now?",
]

cols = st.columns(3)

for index, suggestion in enumerate(suggestions):
    with cols[index % 3]:
        if st.button(
            suggestion,
            key=f"assistant_suggestion_{index}",
            use_container_width=True,
        ):
            st.session_state["pending_question"] = suggestion


# ---------------------------------------------------------------------
# Pending suggestion
# ---------------------------------------------------------------------

pending_question = st.session_state.pop(
    "pending_question",
    None,
)


# ---------------------------------------------------------------------
# Chat history
# ---------------------------------------------------------------------

for message in st.session_state["chat_history"]:

    role = message.get("role", "assistant")
    content = message.get("content", "")

    if role not in ("user", "assistant"):
        continue

    with st.chat_message(role):
        st.markdown(content)


# ---------------------------------------------------------------------
# Chat input
# ---------------------------------------------------------------------

question = st.chat_input(
    "Ask about your soil, irrigation, temperature, humidity or farm status..."
)

if question is None and pending_question:
    question = pending_question


# ---------------------------------------------------------------------
# Process question
# ---------------------------------------------------------------------

if question:

    question = question.strip()

    if question:

        # Add user message.
        st.session_state["chat_history"].append(
            {
                "role": "user",
                "content": question,
            }
        )

        # Generate local sensor-based answer.
        answer = ai_reply(
            question,
            history=st.session_state["chat_history"][:-1],
        )

        # Add assistant response.
        st.session_state["chat_history"].append(
            {
                "role": "assistant",
                "content": answer,
            }
        )

        st.rerun()


# ---------------------------------------------------------------------
# Clear conversation
# ---------------------------------------------------------------------

st.divider()

clear_col, info_col = st.columns([1, 3])

with clear_col:

    if st.button(
        "🗑️ Clear conversation",
        use_container_width=True,
    ):
        st.session_state["chat_history"] = []
        st.rerun()

with info_col:

    st.caption(
        "AgroSentry uses deterministic sensor rules for irrigation and "
        "farm-condition recommendations. It never invents unavailable readings."
    )
