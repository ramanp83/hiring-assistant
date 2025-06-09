import streamlit as st
import os
import json
import datetime
import time
from utils.openai_utils import get_llm_response
from utils.context_utils import update_context, clear_context
from interview_flow import (
    start_tech_evaluation,
    run_interview,
    validate_input,
    classify_experience_level,
)

# ✅ Set page config
st.set_page_config(page_title="TalentScout Hiring Assistant", layout="wide")

# ✅ Load CSS
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ✅ Add header
st.markdown("""
    <div style="text-align: center;">
        <img src="https://cdn-icons-png.flaticon.com/512/18355/18355249.png" width="60" height="60">
        <h1 style="margin: 0.5rem 0;">TalentScout - AI Hiring Assistant</h1>
    </div>
""", unsafe_allow_html=True)

# 🔄 Restart chat button
if st.button("🔄 Restart Chat"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# Predefined questions
candidate_questions = [
    "What is your full name?",
    "Please provide your email address.",
    "Can I have your phone number?",
    "How many years of experience do you have?",
    "What position are you applying for?",
    "Where are you currently located?",
    "List your tech stack (languages, frameworks, tools)."
]

# Initialize session state
for key, default in {
    "messages": [],
    "context": [],
    "candidate_info": {},
    "current_question_index": 0,
    "confirmation_pending": False,
    "info_verified": False,
    "interview_complete": False,
    "greeting_done": False,
    "user_ready": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# Function for typewriter effect
def typewriter_effect(text, delay=0.02):
    placeholder = st.empty()
    full_text = ""
    for char in text:
        full_text += char
        placeholder.markdown(f'<div class="chat-message bot-msg">{full_text}</div>', unsafe_allow_html=True)
        time.sleep(delay)

# Display chat history
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    role_class = "user-msg" if msg["role"] == "user" else "bot-msg"
    st.markdown(f'<div class="chat-message {role_class}">{msg["content"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# 👋 Greet only once
if not st.session_state.greeting_done:
    greeting_text = "Hi there! 😊 I’m TalentScout, your AI hiring assistant.\n\nMay I begin by asking you a few questions?"
    st.session_state.messages.append({"role": "assistant", "content": ""})
    typewriter_effect(greeting_text)
    st.session_state.messages[-1]["content"] = greeting_text
    st.session_state.greeting_done = True

# 📝 Chat input
user_input = st.chat_input("Your answer...")
exit_keywords = ["exit", "stop", "bye", "thank you"]

# 👉 Handle greeting confirmation FIRST
if not st.session_state.user_ready:
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.markdown(f'<div class="chat-message user-msg">{user_input}</div>', unsafe_allow_html=True)

        if user_input.lower() in ["yes", "sure", "okay", "ok", "yep"]:
            st.session_state.user_ready = True
            first_q = candidate_questions[st.session_state.current_question_index]
            st.session_state.messages.append({"role": "assistant", "content": first_q})
            typewriter_effect(first_q)
        else:
            bot_reply = "✅ Just let me know when you're ready to begin by typing `yes`."
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            typewriter_effect(bot_reply)
        st.stop()

# 🧠 Run interview only after info is verified
if st.session_state.info_verified and not st.session_state.interview_complete:
    run_interview()
    st.stop()

# 🧾 Handle normal question flow
if user_input and st.session_state.user_ready:
    user_input = user_input.strip()

    if not user_input:
        st.warning("⚠️ Sorry, I didn’t catch that. Could you please repeat your answer?")
        st.stop()

    if user_input.lower() in exit_keywords:
        st.markdown("👋 Thanks for chatting! We’ll follow up soon. Have a great day!")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": user_input})
    st.markdown(f'<div class="chat-message user-msg">{user_input}</div>', unsafe_allow_html=True)

    if st.session_state.current_question_index < len(candidate_questions) and not st.session_state.confirmation_pending:
        question = candidate_questions[st.session_state.current_question_index]

        if not validate_input(question, user_input):
            bot_reply = "⚠️ **Invalid input. Please try again.**"
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            typewriter_effect(bot_reply)
            st.stop()

        st.session_state.candidate_info[question] = user_input
        st.session_state.context = update_context(st.session_state.context, user_input)
        st.session_state.current_question_index += 1

        if st.session_state.current_question_index < len(candidate_questions):
            next_q = candidate_questions[st.session_state.current_question_index]
            st.session_state.messages.append({"role": "assistant", "content": next_q})
            typewriter_effect(next_q)
            st.stop()
        else:
            summary = "**Here’s the information you provided:**\n\n"
            for question, answer in st.session_state.candidate_info.items():
                summary += f"**{question}**: {answer}\n\n"

            st.session_state.messages.append({"role": "assistant", "content": summary})
            typewriter_effect(summary)

            confirm_msg = "✅ Is all this correct? (yes / no)"
            st.session_state.messages.append({"role": "assistant", "content": confirm_msg})
            typewriter_effect(confirm_msg)

            st.session_state.confirmation_pending = True
            st.stop()

# ✅ Confirmation step
if st.session_state.confirmation_pending and not st.session_state.info_verified:
    if user_input.lower() == "yes":
        st.session_state.info_verified = True
    elif user_input.lower() == "no":
        bot_reply = "🔄 Please restart the chat to re-enter your details."
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        typewriter_effect(bot_reply)
        st.stop()
    else:
        bot_reply = "⚠️ Please reply with `yes` or `no` to confirm the information."
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        typewriter_effect(bot_reply)
        st.stop()

# ✅ Generate technical questions
if st.session_state.info_verified:
    tech_stack = st.session_state.candidate_info.get(candidate_questions[-1], "")
    experience = st.session_state.candidate_info.get("How many years of experience do you have?", "0")
    level = classify_experience_level(experience)
    st.session_state.experience_level = level

    instruction = f"Generate 3 to 5 technical interview questions for the following tech stack: {tech_stack}. Keep them relevant and appropriately challenging."
    reply = get_llm_response(instruction, st.session_state.context)

    st.session_state.messages.append({"role": "assistant", "content": "✅ Thanks! Here are your custom technical questions:"})
    typewriter_effect("✅ Thanks! Here are your custom technical questions:")

    st.session_state.messages.append({"role": "assistant", "content": reply})
    typewriter_effect(reply)

    questions = reply.strip().split("\n\n")
    start_tech_evaluation(questions, experience_level=level)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    name = st.session_state.candidate_info.get("What is your full name?", "anonymous").replace(" ", "_")
    filename = f"candidate_{name}_{timestamp}.json"
    os.makedirs("candidates", exist_ok=True)
    with open(f"candidates/{filename}", "w") as f:
        json.dump(st.session_state.candidate_info, f, indent=4)

    st.success(f"✅ Candidate info saved to: `candidates/{filename}`")
    st.session_state.current_question_index += 1
    st.stop()
