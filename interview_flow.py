# interview_flow.py

import streamlit as st
from utils.openai_utils import get_llm_response
import re

# Initialize states if not already
if "tech_questions" not in st.session_state:
    st.session_state.tech_questions = []

if "tech_question_index" not in st.session_state:
    st.session_state.tech_question_index = 0

if "tech_answers" not in st.session_state:
    st.session_state.tech_answers = []

if "tech_feedback" not in st.session_state:
    st.session_state.tech_feedback = []

if "interview_complete" not in st.session_state:
    st.session_state.interview_complete = False


def start_tech_evaluation(questions, experience_level="beginner"):
    """
    Starts the technical interview evaluation step-by-step.
    questions: list of generated questions.
    experience_level: used to adjust difficulty
    """
    # Adjust question prompt for experience
    adjusted_questions = []
    for q in questions:
        q_prompt = f"[Experience Level: {experience_level.capitalize()}] {q}"
        adjusted_questions.append(q_prompt)

    st.session_state.tech_questions = adjusted_questions
    st.session_state.tech_question_index = 0
    st.session_state.tech_answers = []
    st.session_state.tech_feedback = []
    st.session_state.interview_complete = False
    st.session_state.experience_level = experience_level


def run_interview():
    """
    Run the technical Q&A and feedback loop.
    """
    if st.session_state.interview_complete:
        st.markdown("✅ This interview session has been completed. Restart to begin again.")
        return

    if st.session_state.tech_question_index >= len(st.session_state.tech_questions):
        st.session_state.interview_complete = True

        st.success("✅ Interview complete! 🎉")
        with st.chat_message("assistant"):
            st.markdown("👋 Thank you for participating in the interview process.")
            st.markdown("📩 We’ll review your responses and get back to you with next steps shortly.")
            st.markdown("Feel free to close this window or click **🔄 Restart** to begin again.")

        for i, (q, a, f) in enumerate(zip(
            st.session_state.tech_questions,
            st.session_state.tech_answers,
            st.session_state.tech_feedback,
        )):
            st.markdown(f"---\n**Q{i+1}:** {q}")
            st.markdown(f"**Your Answer:** {a}")
            st.markdown(f"**Feedback:** {f}")
        return

    # Current question
    current_q = st.session_state.tech_questions[st.session_state.tech_question_index]
    st.markdown(f"**Experience Level:** {st.session_state.get('experience_level', 'Not specified')}")
    st.markdown(f"**Question {st.session_state.tech_question_index + 1}:** {current_q}")

    user_answer = st.chat_input("Your answer to the above question...")

    if user_answer:
        st.session_state.tech_answers.append(user_answer)

        # Ask LLM to evaluate the answer
        prompt = f"""
        You are an AI interview coach. Evaluate the following candidate's answer to a technical question.

        Question: {current_q}
        Answer: {user_answer}

        Provide feedback in 2-3 sentences, focusing on correctness, completeness, and areas of improvement.
        """
        feedback = get_llm_response(prompt, [])
        st.session_state.tech_feedback.append(feedback)

        with st.chat_message("assistant"):
            st.markdown("**Feedback:**")
            st.markdown(feedback)

        st.session_state.tech_question_index += 1
        st.rerun()


def validate_input(question, answer):
    import re
    q = question.lower()
    a = answer.strip()

    # Name validation: Only alphabets and spaces, no digits/special characters
    if "full name" in q:
        return bool(re.match(r"^[A-Za-z ]+$", a)) and len(a.split()) >= 2

    # Email validation: Must include '@gmail.com'
    if "email" in q:
        return bool(re.match(r"^[\w.-]+@gmail\.com$", a))

    # Phone number: Must be exactly 10 digits
    if "phone" in q or "mobile" in q:
        return bool(re.match(r"^\d{10}$", a))

    # Experience: Allow digits or keywords
    if "experience" in q:
        return bool(re.search(r"(\d+|fresher|junior|senior|lead|expert|beginner)", a.lower()))

    # Tech stack: At least 3 characters, no digits only
    if "tech stack" in q or "position" in q or "location" in q:
        return bool(re.match(r"^[A-Za-z ,\-/()]+$", a))

    # '''
    # Only alphabets, spaces, commas, dashes, slashes, and parentheses are allowed. 
    # Numeric-only or symbol-heavy responses will trigger a validation error
    # for this question:
    #     "What position are you applying for?"
    #     "Where are you currently located?"
    #     "List your tech stack (languages, frameworks, tools)."
    # '''
    # if "position" in q or "location" in q or "tech stack" in q:
    #     return bool(re.match(r"^[A-Za-z ,\-/()]+$", a)) and len(a) >= 3



    # Default: accept all
    return True


def classify_experience_level(experience_str):
    experience_str = experience_str.lower().strip()

    if any(keyword in experience_str for keyword in ["fresher", "beginner", "entry", "junior"]):
        return "beginner"
    if any(keyword in experience_str for keyword in ["senior", "expert", "lead", "architect"]):
        return "advanced"

    match = re.search(r"\d+", experience_str)
    years = int(match.group()) if match else 0

    if years >= 4:
        return "advanced"
    elif years >= 2:
        return "intermediate"
    else:
        return "beginner"
