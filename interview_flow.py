# interview_flow.py

import streamlit as st
from utils.openai_utils import get_llm_response

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
