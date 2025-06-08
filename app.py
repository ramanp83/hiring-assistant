import streamlit as st
import os
import json
import datetime
from utils.openai_utils import get_llm_response
from utils.context_utils import update_context, clear_context
from interview_flow import start_tech_evaluation, run_interview  # Importing the interview module
import re

# Page setup
st.set_page_config(page_title="TalentScout Hiring Assistant", layout="wide")
st.title("🤖 TalentScout - AI Hiring Assistant")
st.markdown("Hi! I'm here to help screen candidates. Let's get started! 🚀")

# 🔄 Restart if st.button("🔄 Restart Chat"):
if st.button("🔄 Restart Chat"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# Question list
candidate_questions = [
    "What is your full name?",
    "Please provide your email address.",
    "Can I have your phone number?",
    "How many years of experience do you have?",
    "What position are you applying for?",
    "Where are you currently located?",
    "List your tech stack (languages, frameworks, tools)."
]

# Init state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "context" not in st.session_state:
    st.session_state.context = []

if "candidate_info" not in st.session_state:
    st.session_state.candidate_info = {}

if "current_question_index" not in st.session_state:
    st.session_state.current_question_index = 0

if "confirmation_pending" not in st.session_state:
    st.session_state.confirmation_pending = False

if "info_verified" not in st.session_state:
    st.session_state.info_verified = False

# Display history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle input
user_input = st.chat_input("Your answer...")

exit_keywords = ["exit", "stop", "bye", "thank you"]
if user_input:
    user_input = user_input.strip()

    if not user_input:
        with st.chat_message("assistant"):
            st.markdown("⚠️ Sorry, I didn’t catch that. Could you please repeat your answer?")
        st.stop()

    if user_input.lower() in exit_keywords:
        with st.chat_message("assistant"):
            st.markdown("👋 Thanks for chatting! We’ll follow up soon. Have a great day!")
        st.stop()

    # Show user input
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Info collection phase
    if (st.session_state.current_question_index < len(candidate_questions)
            and not st.session_state.confirmation_pending):
        # Save answer
        q_key = candidate_questions[st.session_state.current_question_index]
        st.session_state.candidate_info[q_key] = user_input
        st.session_state.context = update_context(st.session_state.context, user_input)
        st.session_state.current_question_index += 1

        # Ask next question
        if st.session_state.current_question_index < len(candidate_questions):
            next_q = candidate_questions[st.session_state.current_question_index]
            with st.chat_message("assistant"):
                st.markdown(next_q)
            st.stop()

        # End of questions → Show summary
        else:
            summary = "**Here’s the information you provided:**\n\n"
            for question, answer in st.session_state.candidate_info.items():
                summary += f"**{question}**: {answer}\n\n"

            with st.chat_message("assistant"):
                st.markdown(summary)
                st.markdown("✅ Is all this correct? (yes / no)")

            st.session_state.confirmation_pending = True
            st.stop()

    # Handle confirmation
    if st.session_state.confirmation_pending and not st.session_state.info_verified:
        if user_input.lower() == "yes":
            st.session_state.info_verified = True
        elif user_input.lower() == "no":
            with st.chat_message("assistant"):
                st.markdown("🔄 Please restart the chat to re-enter your details.")
            st.stop()
        else:
            with st.chat_message("assistant"):
                st.markdown("⚠️ Please reply with `yes` or `no` to confirm the information.")
            st.stop()

    # Generate technical questions
    if st.session_state.info_verified:
        tech_stack = st.session_state.candidate_info.get(candidate_questions[-1], "")
        instruction = f"Generate 3 to 5 technical interview questions for the following tech stack: {tech_stack}. Keep them relevant and appropriately challenging."

        reply = get_llm_response(instruction, st.session_state.context)
        st.session_state.messages.append({"role": "assistant", "content": reply})

        with st.chat_message("assistant"):
            st.markdown("✅ Thanks! Here are your custom technical questions:")
            st.markdown(reply)

        # Extract experience
        experience = st.session_state.candidate_info.get("How many years of experience do you have?", "0")
        
        # Extract numeric part safely from experience string
        match = re.search(r'\d+', experience)
        years = int(match.group()) if match else 0

        # Assign level
        level = "advanced" if years >= 4 else "intermediate" if years >= 2 else "beginner"

        questions = reply.strip().split("\n\n")  # Assuming LLM gives 1 question per block

        start_tech_evaluation(questions, experience_level=level)
        run_interview()  # Run the interview after technical evaluation

        # Save candidate info
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        name = st.session_state.candidate_info.get("What is your full name?", "anonymous").replace(" ", "_")
        filename = f"candidate_{name}_{timestamp}.json"
        os.makedirs("candidates", exist_ok=True)

        with open(f"candidates/{filename}", "w") as f:
            json.dump(st.session_state.candidate_info, f, indent=4)

        st.success(f"✅ Candidate info saved to: `candidates/{filename}`")

        st.session_state.current_question_index += 1  # lock state
        st.stop()

# Display initial question on first load
if (st.session_state.current_question_index < len(candidate_questions)
        and not st.session_state.confirmation_pending
        and user_input is None):
    current_q = candidate_questions[st.session_state.current_question_index]
    with st.chat_message("assistant"):
        st.markdown(current_q)
