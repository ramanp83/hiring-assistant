import streamlit as st
from utils.openai_utils import get_llm_response
from utils.context_utils import update_context, clear_context

# Page config
st.set_page_config(page_title="TalentScout Hiring Assistant", layout="wide")

# Title
st.title("🤖 TalentScout - AI Hiring Assistant")
st.markdown("Hi! I'm here to help screen candidates. Let's get started! 🚀")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "context" not in st.session_state:
    st.session_state.context = []

# Chat input
user_input = st.chat_input("Say something...")

# Show chat history
for msg in st.session_state.messages:
    role = msg["role"]
    with st.chat_message(role):
        st.markdown(msg["content"])

# Handle user input
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Update context
    st.session_state.context = update_context(st.session_state.context, user_input)
    
    # Generate bot reply using LLM
    reply = get_llm_response(user_input, st.session_state.context)
    
    # Show response
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)

    # End conversation logic
    if any(word in user_input.lower() for word in ["bye", "thank you", "exit", "stop"]):
        st.markdown("👋 Thanks for chatting. We'll reach out soon!")
        clear_context()
