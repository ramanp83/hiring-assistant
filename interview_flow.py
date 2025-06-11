import streamlit as st
from utils.openai_utils import get_llm_response
from prompts.prompt_templates import TECH_FEEDBACK_PROMPT, SENTIMENT_ANALYSIS_PROMPT
import re
<<<<<<< HEAD
import logging
=======
from prompts.prompt_templates import TECH_FEEDBACK_PROMPT, SENTIMENT_ANALYSIS_PROMPT
import time
>>>>>>> 53eb06b (solve error, working on LLM, Feedback, and improve UI.)

logging.basicConfig(filename="talentscout.log", level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

def start_tech_evaluation(questions, experience_level="beginner"):
    """Initialize the technical interview."""
    adjusted_questions = []
    for q in questions:
        q_cleaned = re.sub(r"^\[Experience Level: [A-Za-z]+\]\s*", "", q)
        adjusted_questions.append(q_cleaned)

    st.session_state.tech_questions = adjusted_questions
    st.session_state.tech_question_index = 0
    st.session_state.tech_answers = []
    st.session_state.tech_feedback = []
    st.session_state.interview_complete = False
    st.session_state.experience_level = experience_level
    logging.debug(f"Technical evaluation started with questions: {adjusted_questions}")

def analyze_sentiment(text):
    """Analyze sentiment of the answer."""
    prompt = SENTIMENT_ANALYSIS_PROMPT.format(text=text)
    response = get_llm_response(prompt, [])
    response = response.strip().lower()
    sentiment = "Neutral"
    if "positive" in response:
        sentiment = "Positive"
    elif "negative" in response:
        sentiment = "Negative"
    logging.debug(f"Sentiment analysis result: {sentiment}")
    return sentiment

def run_interview(container):
    """Run the technical Q&A and feedback loop."""
    exit_keywords = ["exit", "stop", "bye", "thank you"]

    # Check if interview is complete
    if st.session_state.interview_complete:
        with container:
            st.session_state.messages.append({
                "role": "assistant",
                "content": "✅ This interview session has been completed.\n\n"
                           "👋 Thank you for participating in the interview process.\n"
                           "📩 We’ll review your responses and get back to you with next steps shortly.\n"
                           "### What would you like to do next?\n"
                           "- Click the **🔄 Restart** button at the top to start over."
            })
            # Display summary
            summary = ""
            for i, (q, a, f) in enumerate(zip(
                st.session_state.tech_questions,
                st.session_state.tech_answers,
                st.session_state.tech_feedback,
            ), 1):
                feedback_content = f.replace("[Assistant]: **Feedback:**\n", "")
                summary += f"---\n**Q{i}:** {q}\n**Your Answer:** {a}\n**Feedback:** {feedback_content}\n"
            st.session_state.messages.append({"role": "assistant", "content": summary})
        logging.info("Interview completed and summary displayed")
        return

    # Check if all questions are answered
    if st.session_state.tech_question_index >= len(st.session_state.tech_questions):
        st.session_state.interview_complete = True
        with container:
            st.session_state.messages.append({"role": "assistant", "content": "✅ Interview complete! 🎉"})
        logging.info("All technical questions answered")
        return

    # Display current question
    experience_level = st.session_state.get('experience_level', 'beginner')
    current_q = st.session_state.tech_questions[st.session_state.tech_question_index]
    question_text = f"**Experience Level:** {experience_level.capitalize()}\n**Question {st.session_state.tech_question_index + 1}:** {current_q}"
    if not any(msg["content"] == question_text for msg in st.session_state.messages):
        st.session_state.messages.append({"role": "assistant", "content": question_text})
        with container:
            st.markdown(f'<div class="chat-message bot-msg">{question_text}</div>', unsafe_allow_html=True)
        logging.debug(f"Displayed question: {current_q}")

    # Handle user answer
    with container:
        user_answer = st.chat_input("Your answer to the above question...", key=f"tech_input_{st.session_state.tech_question_index}")

<<<<<<< HEAD
    if not user_answer or user_answer == st.session_state.get("last_tech_input"):
        return

    logging.info(f"Technical interview user answer: {user_answer}")
    st.session_state.last_tech_input = user_answer
    user_answer = user_answer.strip()

    # Check for exit command
    if user_answer.lower() in exit_keywords:
        st.session_state.messages.append({"role": "user", "content": user_answer})
        st.session_state.messages.append({"role": "assistant", "content": "👋 Goodbye! Thank you for using TalentScout."})
        st.session_state.interview_complete = True
        with container:
            st.markdown('<div class="chat-message user-msg">{user_answer}</div>', unsafe_allow_html=True)
            st.markdown('<div class="chat-message bot-msg">👋 Goodbye! Thank you for using TalentScout.</div>', unsafe_allow_html=True)
        logging.info("User exited technical interview")
        return

    # Append and display user answer
    st.session_state.messages.append({"role": "user", "content": user_answer})
    with container:
        st.markdown(f'<div class="chat-message user-msg">{user_answer}</div>', unsafe_allow_html=True)
    st.session_state.tech_answers.append(user_answer)

    # Sentiment analysis
    with st.spinner("Analyzing response..."):
        sentiment = analyze_sentiment(user_answer)

    # LLM feedback
    prompt = TECH_FEEDBACK_PROMPT.format(question=current_q, answer=user_answer)
    with st.spinner("Generating feedback..."):
=======
    # Empty answer validation
    if user_answer is not None:
        user_answer = user_answer.strip()
        if not user_answer:
            st.warning("⚠️ Please provide an answer before proceeding.")
            st.stop()

        st.session_state.tech_answers.append(user_answer)

        # Use centralized prompt from prompt_templates.py
        prompt = TECH_FEEDBACK_PROMPT.format(answer=user_answer)
>>>>>>> 53eb06b (solve error, working on LLM, Feedback, and improve UI.)
        feedback = get_llm_response(prompt, [])

    # Combine sentiment and feedback
    combined_feedback = f"[Assistant]: **Feedback:**\nCandidate sentiment detected: **{sentiment}**.\n\n{feedback}"
    st.session_state.messages.append({"role": "assistant", "content": combined_feedback})
    st.session_state.tech_feedback.append(combined_feedback)

<<<<<<< HEAD
    with container:
        st.markdown(f'<div class="chat-message bot-msg">{combined_feedback}</div>', unsafe_allow_html=True)
    logging.debug(f"Feedback provided: {combined_feedback[:50]}...")
=======
        st.session_state.tech_question_index += 1
        time.sleep(0.1)  # Stable rerun with delay
        st.rerun()
>>>>>>> 53eb06b (solve error, working on LLM, Feedback, and improve UI.)

    # Move to next question
    st.session_state.tech_question_index += 1

def validate_input(question, answer):
    q = question.lower()
    a = answer.strip()

    if "full name" in q:
        return bool(re.match(r"^[A-Za-z ]+$", a)) and len(a.split()) >= 2
    if "email" in q:
        return bool(re.match(r"^[\w.-]+@gmail\.com$", a))
    if "phone" in q or "mobile" in q:
        return bool(re.match(r"^\d{10}$", a))
    if "experience" in q:
        return bool(re.search(r"(\d+|fresher|junior|senior|lead|expert|beginner)", a.lower()))
    if "tech stack" in q or "position" in q or "location" in q:
        return bool(re.match(r"^[A-Za-z ,\-/()]+$", a))
    return True

def classify_experience_level(experience_str):
    experience_str = experience_str.lower().strip()
    if any(keyword in experience_str for keyword in ["fresher", "beginner", "entry", "junior"]):
        return "beginner"
    if any(keyword in experience_str for keyword in ["senior", "expert", "lead", "architect"]):
        return "advanced"
    match = re.search(r"\d+", experience_str)
    years = int(match.group()) if match else 0
    return "advanced" if years >= 4 else "intermediate" if years >= 2 else "beginner"