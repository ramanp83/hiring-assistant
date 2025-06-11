# Default technical questions for fallback
DEFAULT_TECH_QUESTIONS = [
    "Write a Python function to find the maximum value in a list of integers. The function should handle empty lists and lists containing only one element.",
    "Describe a challenging bug you encountered in your projects and how you resolved it.",
    "What are the key differences between lists and tuples in Python, and when would you use each?"
]

# Prompt for generating technical questions
TECH_QUESTION_PROMPT = """
You are an AI hiring assistant. Generate 3 to 5 technical interview questions for the following tech stack: {stack}.
The candidate has {exp} years of experience.
Make questions tailored to this profile.
Format the questions as a numbered list (e.g., '1. Question text', '2. Question text').
Do not include any introductory text or preamble.
"""

# Prompt for generating feedback on technical answers
TECH_FEEDBACK_PROMPT = """
You are an AI interview coach. Evaluate the following candidate's answer to a technical question.

Question: {question}
Answer: {answer}

Provide feedback in 2-3 sentences, focusing on correctness, completeness, and areas of improvement.
"""

# Prompt for sentiment analysis
SENTIMENT_ANALYSIS_PROMPT = """
Analyze the sentiment of this text and return one word from Positive, Neutral, or Negative:

{text}
"""