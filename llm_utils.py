import json
import os

import google.generativeai as genai
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
                {"role": "system", "content": "You are a helpful AI that strictly outputs raw JSON arrays."},
                {"role": "user", "content": prompt}
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
    except Exception as e:
        print(f"Error generating questions from Groq: {e}")
        return []

def generate_gemini_questions(topic: str, count: int = 5) -> list:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return []
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
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
    
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.7
            )
        )
        data = json.loads(response.text)
        return data
    except Exception as e:
        print(f"Error generating questions from Gemini: {e}")
        return []
