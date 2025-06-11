# Context tracking

def update_context(context, user_input):
    context.append(user_input)
    return context

def clear_context():
    import streamlit as st
<<<<<<< HEAD
    st.session_state.messages = []
    st.session_state.context = []
    # Reset other relevant session state variables
    for key in [
        "candidate_info",
        "current_question_index",
        "confirmation_pending",
        "info_verified",
        "interview_complete",
        "greeting_done",
        "user_ready",
        "tech_questions",
        "tech_question_index",
        "tech_answers",
        "tech_feedback",
        "edit_mode",
        "edit_question"
    ]:
        if key in st.session_state:
            st.session_state[key] = {
                "messages": [],
                "context": [],
                "candidate_info": {},
                "current_question_index": 0,
                "confirmation_pending": False,
                "info_verified": False,
                "interview_complete": False,
                "greeting_done": False,
                "user_ready": False,
                "tech_questions": [],
                "tech_question_index": 0,
                "tech_answers": [],
                "tech_feedback": [],
                "edit_mode": False,
                "edit_question": None
            }.get(key)
=======
    # Comprehensive reset of all relevant session state variables
    defaults = {
        "messages": [],
        "context": [],
        "candidate_info": {},
        "current_question_index": 0,
        "confirmation_pending": False,
        "info_verified": False,
        "interview_complete": False,
        "greeting_done": False,
        "user_ready": False,
        "edit_mode": False,
        "edit_question": None,
        "pre_interview_confirmed": False,
        "tech_questions": [],
        "tech_question_index": 0,
        "tech_answers": [],
        "tech_feedback": [],
        "experience_level": None,
    }
    for key, value in defaults.items():
        st.session_state[key] = value
>>>>>>> 53eb06b (solve error, working on LLM, Feedback, and improve UI.)
