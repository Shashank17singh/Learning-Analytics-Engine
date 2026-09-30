import json
import os

import google.generativeai as genai
import streamlit as st
from groq import Groq


def generate_groq_questions(topic: str, count: int = 5) -> list:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return []

    client = Groq(api_key=api_key)

    prompt = f"""
    Generate exactly {count} multiple-choice questions about the topic '{topic}'.
    Return the response strictly as a JSON array of objects. Do not include markdown formatting or backticks around the JSON.
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

    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful AI that strictly outputs raw JSON arrays.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )
        response_text = completion.choices[0].message.content
        if response_text.startswith("`json"):
            response_text = response_text[7:]
        if response_text.endswith("`"):
            response_text = response_text[:-3]

        data = json.loads(response_text.strip())
        return data
    except Exception as e:  # noqa: BLE001
        print(f"Error generating questions from Groq: {e}")
        return []


def generate_gemini_questions(topic: str, count: int = 5) -> list:
    try:
        api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
    except Exception:  # noqa: BLE001
        api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return []

    genai.configure(api_key=api_key)

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
        "gemini-1.5-flash",
        "gemini-1.5-flash-latest",
        "gemini-2.0-flash-exp",
        "gemini-1.5-pro",
        "gemini-1.5-pro-latest",
        "gemini-1.5-flash-8b",
        "gemini-1.0-pro",
        "gemini-pro",
    ]

    last_error = None
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            if "pro" in model_name and "1.5" not in model_name:
                response = model.generate_content(
                    prompt,
                    generation_config=genai.GenerationConfig(temperature=0.7),
                )
            else:
                response = model.generate_content(
                    prompt,
                    generation_config=genai.GenerationConfig(
                        response_mime_type="application/json", temperature=0.7
                    ),
                )

            response_text = response.text.strip()
            response_text = response_text.removeprefix("```json")
            response_text = response_text.removesuffix("```")

            data = json.loads(response_text.strip())
            return data
        except Exception as e:  # noqa: BLE001
            last_error = e
            if "404" in str(e):
                continue
            else:
                st.error(f"Google Generative AI API Error ({model_name}): {e!s}")
                print(f"Error generating questions from Gemini ({model_name}): {e}")
                return []

    try:
        all_models = list(genai.list_models())
        available_models = [
            m.name
            for m in all_models
            if "generateContent" in m.supported_generation_methods
        ]

        if not available_models:
            model_names = [m.name for m in all_models]
            msg = f"Your API Key has no models supporting generateContent. Available: {', '.join(model_names)}"
            st.error(msg)
            print(msg)
            return []

        first_model = available_models[0].replace("models/", "")
        model = genai.GenerativeModel(first_model)

        response = model.generate_content(prompt)
        response_text = response.text.strip()
        response_text = response_text.removeprefix("```json")
        response_text = response_text.removesuffix("```")
        return json.loads(response_text.strip())

    except Exception as e:  # noqa: BLE001
        try:
            model_names = [m.name for m in genai.list_models()]
            print(
                f"Fallback model discovery failed: {e}. Available models: {model_names}"
            )
        except Exception:  # noqa: BLE001
            print(f"Fallback model discovery failed completely: {e}")

    if last_error:
        st.error(f"Google Generative AI API Error: {last_error!s}")
        print(
            f"Error generating questions from Gemini (all models failed): {last_error}"
        )
    return []
