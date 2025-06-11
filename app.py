import streamlit as st
import os
import json
import datetime
import time
import re
import logging
from langdetect import detect
from utils.openai_utils import get_llm_response
from utils.context_utils import update_context, clear_context
from interview_flow import (
    start_tech_evaluation,
    run_interview,
    validate_input,
    classify_experience_level,
)
from prompts.prompt_templates import DEFAULT_TECH_QUESTIONS, TECH_QUESTION_PROMPT

# Configure logging
logging.basicConfig(filename="talentscout.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Set page config
st.set_page_config(page_title="TalentScout Hiring Assistant", layout="wide")

# Load CSS
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Add header
st.markdown("""
    <div style="text-align: center;">
        <img src="https://cdn-icons-png.flaticon.com/512/18355/18355249.png" width="60" height="60">
        <h1 style="margin: 0.5rem 0;">TalentScout - AI Hiring Assistant</h1>
    </div>
""", unsafe_allow_html=True)

# Restart chat button
if st.button("🔄 Restart Chat"):
    logging.info("User initiated chat restart")
    clear_context()
    st.session_state.clear()
    # Initialize session state again
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
        "user_lang": "en",
        "tech_questions": [],
        "tech_question_index": 0,
        "tech_answers": [],
        "tech_feedback": [],
        "experience_level": "beginner",
        "edit_mode": False,
        "edit_question": None,
        "tech_interview_ready": False,
    }.items():
        st.session_state[key] = default

# Ensure session state is initialized
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
    "user_lang": "en",
    "tech_questions": [],
    "tech_question_index": 0,
    "tech_answers": [],
    "tech_feedback": [],
    "experience_level": "beginner",
    "edit_mode": False,
    "edit_question": None,
    "tech_interview_ready": False,
    "last_input": None,  # Track last input to prevent duplicate processing
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

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

# Helper functions
def detect_language(text):
    try:
        lang = detect(text)
        logging.info(f"Detected language: {lang}")
        return lang
    except Exception as e:
        logging.error(f"Language detection failed: {str(e)}")
        return "en"

def translate_text(text, target_lang):
    prompt = f"Translate the following text to {target_lang}:\n\n{text}"
    translation = get_llm_response(prompt, [])
    logging.debug(f"Translated text to {target_lang}: {translation}")
    return translation.strip()

def typewriter_effect(text, container):
    """Display message in a container with minimal delay."""
    with container:
        st.markdown(f'<div class="chat-message bot-msg">{text}</div>', unsafe_allow_html=True)
    logging.debug(f"Rendered bot message: {text[:50]}...")

def parse_technical_questions(llm_response):
    lines = llm_response.strip().split("\n")
    questions = []
    current_question = ""

    for line in lines:
        line = line.strip()
        if not line or "here are" in line.lower() or "based on" in line.lower() or "technical interview questions" in line.lower():
            continue
        if re.match(r"^\d+\.?\s|^\d+\)\s|^[-*]\s", line):
            if current_question:
                questions.append(current_question.strip())
            current_question = re.sub(r"^\d+\.?\s|^\d+\)\s|^[-*]\s", "", line)
        else:
            current_question += " " + line

    if current_question:
        questions.append(current_question.strip())

    questions = [q for q in questions if q and len(q) > 10 and not q.lower().startswith("question")]
    logging.info(f"Parsed technical questions: {questions}")
    return questions[:5] or DEFAULT_TECH_QUESTIONS

def render_chat_history(container):
    """Render chat history in a container."""
    with container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for msg in st.session_state.messages:
            role_class = "user-msg" if msg["role"] == "user" else "bot-msg"
            st.markdown(f'<div class="chat-message {role_class}">{msg["content"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    logging.debug("Chat history rendered")

def personalized_greeting():
    """Generate a personalized greeting based on candidate info."""
    name = st.session_state.candidate_info.get("What is your full name?", "")
    greeting = f"Welcome back, {name}! Ready to continue your interview?" if name else "Hi there! 😊 I’m TalentScout, your AI hiring assistant.\n\nMay I begin by asking you a few questions?"
    return greeting

def handle_exit(user_input):
    """Handle exit keywords."""
    exit_keywords = ["exit", "stop", "bye", "thank you"]
    if not user_input:
        return False
    if user_input.lower() in exit_keywords:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.messages.append({"role": "assistant", "content": "👋 Thanks for chatting! We’ll follow up soon. Have a great day!"})
        st.session_state.interview_complete = True
        logging.info("User exited the chat")
        return True
    return False

def main():
  """Main app logic for handling conversation flow."""
    chat_container = st.container()
    input_container = st.container()
    spinner_placeholder = st.empty()
    chat_placeholder = st.empty()
    input_placeholder = st.empty()

    def render_chat():
        with chat_placeholder:
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            for msg in st.session_state.messages:
                role_class = "user-msg" if msg["role"] == "user" else "bot-msg"
                st.markdown(f'<div class="chat-message {role_class}">{msg["content"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    render_chat()

    # Display greeting if not done
    if not st.session_state.greeting_done:
        greeting_text = personalized_greeting()
        st.session_state.messages.append({"role": "assistant", "content": greeting_text})
        typewriter_effect(greeting_text, chat_container)
        st.session_state.greeting_done = True
        return

    # Skip processing if interview is complete
    if st.session_state.interview_complete:
        return

    # Single chat input
    with input_container:
        user_input = st.chat_input("Your answer...", key="chat_input")

    if not user_input or user_input == st.session_state.last_input:
        return

    logging.info(f"Processing user input: {user_input}")
    st.session_state.last_input = user_input
    user_input = user_input.strip()

    # Append and display user input
    st.session_state.messages.append({"role": "user", "content": user_input})
    render_chat_history(chat_container)

    # Handle exit
    if handle_exit(user_input):
        return

    # Handle greeting confirmation
    if not st.session_state.user_ready:
        user_lang = detect_language(user_input)
        st.session_state["user_lang"] = user_lang
        if user_input.lower() in ["yes", "sure", "okay", "ok", "yep"]:
            st.session_state.user_ready = True
            first_q = candidate_questions[st.session_state.current_question_index]
            st.session_state.messages.append({"role": "assistant", "content": first_q})
            typewriter_effect(first_q)
        else:
            bot_reply = "✅ Just let me know when you're ready to begin by typing `yes`."
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            typewriter_effect(bot_reply)
        return

    # Handle candidate info collection
    if st.session_state.user_ready and not st.session_state.info_verified:
        if not user_input:
            bot_reply = "⚠️ Sorry, I didn’t catch that. Could you please repeat your answer?"
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            typewriter_effect(bot_reply, chat_container)
            return

        if st.session_state.edit_mode:
            question = st.session_state.edit_question
            if not validate_input(question, user_input):
                bot_reply = "⚠️ Invalid input. Please try again."
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                typewriter_effect(bot_reply, chat_container)
                return
            st.session_state.candidate_info[question] = user_input
            st.session_state.context = update_context(st.session_state.context, user_input)
            st.session_state.edit_mode = False
            st.session_state.edit_question = None
            bot_reply = f"✅ Updated {question} successfully. Please review the updated information."
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            typewriter_effect(bot_reply, chat_container)
        elif st.session_state.current_question_index < len(candidate_questions) and not st.session_state.confirmation_pending:
            question = candidate_questions[st.session_state.current_question_index]
            if not validate_input(question, user_input):
                bot_reply = "⚠️ Invalid input. Please try again."
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                typewriter_effect(bot_reply, chat_container)
                return
            st.session_state.candidate_info[question] = user_input
            st.session_state.context = update_context(st.session_state.context, user_input)
            st.session_state.current_question_index += 1

            if st.session_state.current_question_index < len(candidate_questions):
                next_q = candidate_questions[st.session_state.current_question_index]
                st.session_state.messages.append({"role": "assistant", "content": next_q})
                typewriter_effect(next_q, chat_container)
                return
            else:
                summary = "**Here’s the information you provided:**\n\n"
                for i, (question, answer) in enumerate(st.session_state.candidate_info.items(), 1):
                    summary += f"{i}. **{question}**: {answer}\n\n"
                summary += "✅ Is all this correct? (Type `yes`, `no`, or `edit [number]` to modify a specific answer, e.g., `edit 1` for name.)"
                st.session_state.messages.append({"role": "assistant", "content": summary})
                typewriter_effect(summary, chat_container)
                st.session_state.confirmation_pending = True
                return

    # Handle confirmation
    if st.session_state.confirmation_pending and not st.session_state.info_verified:
        user_input_lower = user_input.lower()
        if user_input_lower == "yes":
            st.session_state.info_verified = True
            bot_reply = "✅ Great! Are you ready to start the technical interview? (Type `yes` to proceed.)"
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            typewriter_effect(bot_reply, chat_container)
            return
        elif user_input_lower == "no":
            bot_reply = "🔄 Please restart the chat to re-enter your details."
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            typewriter_effect(bot_reply, chat_container)
            return
        elif user_input_lower.startswith("edit"):
            try:
                q_index = int(user_input_lower.split()[1]) - 1
                if 0 <= q_index < len(candidate_questions):
                    question = candidate_questions[q_index]
                    st.session_state.edit_mode = True
                    st.session_state.edit_question = question
                    bot_reply = f"Please provide the updated answer for: **{question}**"
                    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                    typewriter_effect(bot_reply, chat_container)
                    return
                else:
                    bot_reply = "⚠️ Invalid question number. Please type `edit [number]` (e.g., `edit 1` for name)."
                    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                    typewriter_effect(bot_reply, chat_container)
                    return
            except:
                bot_reply = "⚠️ Please type `edit [number]` (e.g., `edit 1` for name)."
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                typewriter_effect(bot_reply, chat_container)
                return
        else:
            bot_reply = "⚠️ Please reply with `yes`, `no`, or `edit [number]` to confirm or modify the information."
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            typewriter_effect(bot_reply, chat_container)
            return
        
    # Generate technical questions
    if st.session_state.info_verified and not st.session_state.tech_questions and not st.session_state.tech_interview_ready:
        if user_input.lower() not in ["yes", "sure", "okay", "ok", "yep"]:
            bot_reply = "⚠️ Please type `yes` to start the technical interview."
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            typewriter_effect(bot_reply, chat_container)
            return

        stack = st.session_state.candidate_info.get(candidate_questions[-1], "")
        exp = st.session_state.candidate_info.get("How many years of experience do you have?", "0")
        level = classify_experience_level(exp)
        st.session_state.experience_level = level

        with st.spinner("Generating technical questions..."):
            reply = get_llm_response(TECH_QUESTION_PROMPT.format(stack=stack, exp=exp), st.session_state.context)
            tech_questions = parse_technical_questions(reply)

        st.session_state.messages.append({"role": "assistant", "content": "✅ Thanks! Let’s begin the technical interview."})
        typewriter_effect("✅ Thanks! Let’s begin the technical interview.", chat_container)

        st.session_state.tech_questions = tech_questions
        start_tech_evaluation(st.session_state.tech_questions, experience_level=level)
        # Save candidate file
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        name = st.session_state.candidate_info.get("What is your full name?", "anonymous").replace(" ", "_")
        filename = f"candidates/candidate_{name}_{timestamp}.json"
        os.makedirs("candidates", exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(st.session_state.candidate_info, f, indent=2)
        with chat_container:
            st.success(f"✅ Candidate info saved to: `{filename}`")
        logging.info(f"Candidate info saved to: {filename}")

        st.session_state.tech_interview_ready = True
        return

# Create main container and run logic
main_container = st.container()
with main_container:
    main()

# Run technical interview if ready
if not st.session_state.interview_complete and st.session_state.info_verified and st.session_state.tech_questions and st.session_state.tech_interview_ready:
    with main_container:
        run_interview()