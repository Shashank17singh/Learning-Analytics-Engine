import json
import os

import streamlit as st
from google import genai
from google.genai import types


def generate_gemini_questions(topic: str, count: int = 5) -> list:
    try:
        api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
    except Exception:  # noqa: BLE001
        api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        st.error("GEMINI_API_KEY is not set. Add it to .streamlit/secrets.toml.")
        return []

    client = genai.Client(api_key=api_key)

    prompt = f"""
    Generate exactly {count} multiple-choice questions about the topic '{topic}'.
    Return the response strictly as a JSON array of objects.
    Each object must have exactly these keys:
    - "qno": integer
    - "ques": string (the question)
    - "a": string (option A)
    - "b": string (option B)
    - "c": string (option C)
    - "d": string (option D)
    - "correct": string (the exact text of the correct option)
    - "explanation": string (why it is correct)
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
                st.error(f"Gemini API Error ({model_name}): {e!s}")
                print(f"Error generating questions ({model_name}): {e}")
                return []

    if last_error:
        error_str = str(last_error)
        if "503" in error_str or "429" in error_str:
            st.warning(
                "All models are temporarily overloaded. Please try again in a few seconds."
            )
        else:
            st.error(f"Gemini API Error: {last_error!s}")
        print(f"All models failed. Last error: {last_error}")
    return []
