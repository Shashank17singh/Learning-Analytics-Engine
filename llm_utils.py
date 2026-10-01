import json
import os

import streamlit as st
from google import genai
from google.genai import types


def generate_gemini_questions(topic: str, count: int = 5, difficulty: str = "Medium", context: str = None, exam_format: str = "Standard") -> list:
    try:
        api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
    except Exception:  # noqa: BLE001
        api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        st.error("GEMINI_API_KEY is not set. Add it to .streamlit/secrets.toml.")
        return []

    client = genai.Client(api_key=api_key)

    context_prompt = ""
    if context:
        context_prompt = f"The questions MUST be based strictly on the following source material provided by the student:\n\n{context}\n\n"

    format_instructions = ""
    
    # Categorize exams by their question format requirements
    multi_and_numerical_exams = ["JEE Advanced"]
    mcq_and_numerical_exams = ["JEE Mains", "GATE", "CAT", "BITSAT"] # Note: CAT has TITA (Type In The Answer) which is numerical/text. BITSAT has some numericals in some variants, but mostly MCQ.
    
    if exam_format in multi_and_numerical_exams:
        format_instructions = """
        Generate a mix of Single-Correct MCQs, Multi-Correct MCQs, and Numerical questions.
        For Single-Correct MCQs ("type": "single_mcq"):
        - "options": {"a": "...", "b": "...", "c": "...", "d": "..."}
        - "correct": string (e.g., "a", "b", "c", or "d")
        For Multi-Correct MCQs ("type": "multi_mcq"):
        - "options": {"a": "...", "b": "...", "c": "...", "d": "..."}
        - "correct": array of strings (e.g., ["a", "c"])
        For Numerical/TITA questions ("type": "numerical"):
        - "options": null
        - "correct": string (the exact integer, decimal, or short text answer)
        Each object must have "qno", "type", "ques", "options", "correct", and "explanation".
        """
    elif exam_format in mcq_and_numerical_exams:
        format_instructions = """
        Generate a mix of Single-Correct MCQs (approx 80%) and Numerical/TITA Answer Type questions (approx 20%).
        For Single-Correct MCQs ("type": "single_mcq"):
        - "options": {"a": "...", "b": "...", "c": "...", "d": "..."}
        - "correct": string (e.g., "a", "b", "c", or "d")
        For Numerical/TITA questions ("type": "numerical"):
        - "options": null
        - "correct": string (the exact integer, decimal, or short text answer)
        Each object must have "qno", "type", "ques", "options", "correct", and "explanation".
        """
    else: # Default for Standard, NEET, CLAT, UPSC, NDA, etc.
        format_instructions = """
        Generate ONLY Single-Correct Multiple Choice questions.
        Each object must have:
        - "qno": integer
        - "type": "single_mcq"
        - "ques": string (the question)
        - "options": {"a": "...", "b": "...", "c": "...", "d": "..."}
        - "correct": string (e.g., "a", "b", "c", or "d")
        - "explanation": string
        """

    prompt = f"""
    Generate exactly {count} questions about the topic '{topic}'.
    {context_prompt}
    The difficulty level of the questions must be: {difficulty}.
    Return the response strictly as a JSON array of objects.
    {format_instructions}
    """

    models_to_try = [
        "gemini-3.8-flash",
        "gemini-3.5-flash",
        "gemini-3.7-flash",
        "gemini-3.6-flash",
    ]

    import time

    last_error = None
    for model_name in models_to_try:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.7,
                    ),
                )

                response_text = response.text.strip()
                response_text = response_text.removeprefix("```json")
                response_text = response_text.removesuffix("```")

                data = json.loads(response_text.strip())
                return data
            except Exception as e:  # noqa: BLE001
                last_error = e
                error_str = str(e)
                if "404" in error_str or "not found" in error_str.lower():
                    print(f"Model {model_name} not available, trying next...")
                    break
                if (
                    "503" in error_str
                    or "429" in error_str
                    or "overloaded" in error_str.lower()
                ):
                    print(
                        f"Model {model_name} temporarily unavailable (attempt {attempt + 1}), retrying..."
                    )
                    time.sleep(2)
                    continue
                st.error("System Error: Unable to generate assessment content at this time. Please try again.")
                print(f"Error generating questions ({model_name}): {e}")
                return []

    if last_error:
        error_str = str(last_error)
        if "503" in error_str or "429" in error_str:
            st.warning(
                "All models are temporarily overloaded. Please try again in a few seconds."
            )
        else:
            st.error("System Error: Unable to communicate with the assessment engine.")
        print(f"All models failed. Last error: {last_error}")
    return []

def explain_wrong_answer(question: str, selected_answer: str, correct_answer: str, base_explanation: str) -> str:
    """Generate an explanation specifically addressing why the user's chosen answer is incorrect."""
    try:
        api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
    except Exception:
        api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return base_explanation

    client = genai.Client(api_key=api_key)
    prompt = f"""
    Question: {question}
    Correct Answer: {correct_answer}
    Base Explanation: {base_explanation}
    Student's Incorrect Selection: {selected_answer}

    Provide a concise explanation (2-3 sentences) directly addressing why the student's selected answer is incorrect, and briefly reiterate why the correct answer is right.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.7),
        )
        return response.text.strip()
    except Exception:
        return base_explanation

