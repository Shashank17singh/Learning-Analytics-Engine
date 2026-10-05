import json
import os
import time

import streamlit as st
from google import genai
from google.genai import types


def generate_gemini_questions(
    topic: str,
    count: int = 5,
    difficulty: str = "Medium",
    context: str = None,
    exam_format: str = "Standard",
) -> list:
    """
    Generate assessment questions using the configured AI provider.

    Constructs a detailed prompt with the specified parameters and exam format constraints,
    queries the selected LLM, and parses the returned JSON containing the questions.

    Args:
        topic (str): The subject matter for the generated questions.
        count (int): The number of questions to generate (default is 5).
        difficulty (str): The desired difficulty level of the questions (default is "Medium").
        context (str, optional): Additional contextual information or study material.
        exam_format (str): The target format/style of the exam (default is "Standard").

    Returns:
        list: A list of parsed question dictionaries matching the requested format.
    """
    provider = st.session_state.get("custom_ai_provider", "System Default")
    custom_key = st.session_state.get("custom_api_key", "")

    if provider == "System Default":
        try:
            api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
        except Exception:
            api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            st.error("GEMINI_API_KEY is not set. Add it to .streamlit/secrets.toml.")
            return []
    elif provider in ["Google Gemini", "OpenAI", "Groq", "Anthropic"]:
        if not custom_key:
            st.error(f"Please enter your {provider} API Key in the sidebar.")
            return []
        api_key = custom_key

    context_prompt = (
        f"Use the following study material context to create the questions if relevant:\n{context}"
        if context
        else ""
    )

    format_instructions = ""
    multi_and_numerical_exams = ["JEE Advanced Paper 1", "JEE Advanced Paper 2"]
    mcq_and_numerical_exams = ["JEE Mains", "GATE", "CAT", "BITSAT"]

    if exam_format in multi_and_numerical_exams:
        format_instructions = """
        This is a highly rigorous exam. You MUST generate a mix of these two question types:
        1) "multi_mcq": Multiple Choice Questions where MORE THAN ONE option can be correct. 
           The 'correct' field MUST be a comma-separated string of the correct keys (e.g. "a,c" or "a,b,d").
           Provide exactly 4 options (a, b, c, d).
        2) "numerical": Questions where the answer is a numerical value (integer or decimal).
           Do NOT provide options. Leave 'options' as an empty object {}.
           The 'correct' field MUST be the exact numerical string (e.g. "4.5" or "12").
        
        Randomly mix these two types. Do NOT generate standard single-choice MCQs.
        """
    elif exam_format in mcq_and_numerical_exams:
        format_instructions = """
        You MUST generate a mix of these two question types:
        1) "single_mcq": Standard Multiple Choice Questions with exactly ONE correct option.
           Provide exactly 4 options (a, b, c, d). The 'correct' field must be a single letter.
        2) "numerical": Questions where the answer is a numerical value (integer or decimal).
           Do NOT provide options. Leave 'options' as an empty object {}.
           The 'correct' field MUST be the exact numerical string (e.g. "4.5" or "12").
        """
    else:
        format_instructions = """
        You MUST generate ONLY "single_mcq" type questions.
        Provide exactly 4 options (a, b, c, d).
        The 'correct' field MUST be exactly one of the keys (e.g. "a").
        """

    prompt = f"""
    Generate exactly {count} questions about the topic '{topic}'.
    {context_prompt}
    The difficulty level of the questions must be: {difficulty}.
    Return the response strictly as a JSON array of objects. Do not include markdown code block formatting like ```json.
    {format_instructions}
    
    Each object must have:
    - "qno": integer
    - "type": string (must be one of: "single_mcq", "multi_mcq", "numerical")
    - "ques": string (the question)
    - "options": object with keys "a", "b", "c", "d" (or empty {{}} for numerical)
    - "correct": string
    - "explanation": string
    """

    try:
        if provider in ["System Default", "Google Gemini"]:
            models_to_try = (
                ["gemini-3.8-flash", "gemini-3.5-flash", "gemini-flash-latest"]
                if provider == "System Default"
                else ["gemini-3.8-flash", "gemini-3.5-flash", "gemini-flash-latest"]
            )
            client = genai.Client(api_key=api_key)
            last_error = None
            for model_name in models_to_try:
                for attempt in range(3):
                    try:
                        response = client.models.generate_content(
                            model=model_name,
                            contents=prompt,
                            config=types.GenerateContentConfig(
                                response_mime_type="application/json",
                                temperature=0.7,
                            ),
                        )
                        text = (
                            response.text.strip()
                            .removeprefix("```json\n")
                            .removesuffix("\n```")
                            .removeprefix("```json")
                            .removesuffix("```")
                        )
                        return json.loads(text.strip())
                    except Exception as e:
                        last_error = e
                        if "404" in str(e) or "not found" in str(e).lower():
                            break
                        if (
                            "503" in str(e)
                            or "429" in str(e)
                            or "overloaded" in str(e).lower()
                        ):
                            time.sleep(3)
                            continue
                        raise e
            if last_error:
                raise last_error

        elif provider == "OpenAI":
            import openai

            client = openai.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            text = response.choices[0].message.content.strip()
            text = (
                text.removeprefix("```json\n")
                .removesuffix("\n```")
                .removeprefix("```json")
                .removesuffix("```")
            )
            return json.loads(text.strip())

        elif provider == "Groq":
            import groq

            client = groq.Groq(api_key=api_key)
            response = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            text = response.choices[0].message.content.strip()
            text = (
                text.removeprefix("```json\n")
                .removesuffix("\n```")
                .removeprefix("```json")
                .removesuffix("```")
            )
            return json.loads(text.strip())

        elif provider == "Anthropic":
            import anthropic

            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            text = response.content[0].text.strip()
            text = (
                text.removeprefix("```json\n")
                .removesuffix("\n```")
                .removeprefix("```json")
                .removesuffix("```")
            )
            return json.loads(text.strip())

    except Exception as e:
        error_str = str(e)
        if (
            "503" in error_str
            or "429" in error_str
            or "rate_limit" in error_str.lower()
        ):
            st.warning(
                "The selected AI provider is temporarily overloaded or you hit a rate limit. Please try again later."
            )
        else:
            st.error(
                f"System Error: Unable to communicate with the {provider} engine. Details: {error_str}"
            )
        print(f"Error generating questions ({provider}): {e}")
        return []


def explain_wrong_answer(
    question: str, selected_answer: str, correct_answer: str, base_explanation: str
) -> str:
    """
    Generate a dynamic, targeted explanation for a student's incorrect answer.

    Uses the configured AI provider to create a concise response explaining why the
    student's specific selection was wrong, while reinforcing the correct reasoning.

    Args:
        question (str): The original question text.
        selected_answer (str): The incorrect answer chosen by the student.
        correct_answer (str): The actual correct answer.
        base_explanation (str): The generic explanation for the correct answer.

    Returns:
        str: A dynamically generated explanation addressing the student's specific misconception.
    """
    provider = st.session_state.get("custom_ai_provider", "System Default")
    custom_key = st.session_state.get("custom_api_key", "")

    prompt = f"""
    Question: {question}
    Correct Answer: {correct_answer}
    Base Explanation: {base_explanation}
    Student's Incorrect Selection: {selected_answer}

    Provide a concise explanation (2-3 sentences) directly addressing why the student's selected answer is incorrect, and briefly reiterate why the correct answer is right.
    """

    try:
        if provider in ["System Default", "Google Gemini"]:
            if provider == "System Default":
                api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
                if not api_key:
                    api_key = os.getenv("GEMINI_API_KEY")
                model_name = "gemini-3.8-flash"
            else:
                api_key = custom_key
                model_name = "gemini-3.8-flash"

            if not api_key:
                return base_explanation

            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.3),
            )
            return response.text.strip()

        elif provider == "OpenAI":
            import openai

            client = openai.OpenAI(api_key=custom_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            return response.choices[0].message.content.strip()

        elif provider == "Groq":
            import groq

            client = groq.Groq(api_key=custom_key)
            response = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            return response.choices[0].message.content.strip()

        elif provider == "Anthropic":
            import anthropic

            client = anthropic.Anthropic(api_key=custom_key)
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            return response.content[0].text.strip()

    except Exception as e:
        print(f"Error generating dynamic explanation ({provider}): {e}")
        return base_explanation
