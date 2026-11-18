
import os
from dotenv import load_dotenv
from groq import Groq
from google import genai

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def generate_health_remarks(glucose, haemoglobin, cholesterol):

    prompt = f"""
    You are a health information assistant.

    Explain the following laboratory readings in simple English.

    Glucose: {glucose}
    Haemoglobin: {haemoglobin}
    Total Cholesterol: {cholesterol}

    Instructions:
    1. Explain what each test measures.
    2. Provide general information about the supplied values.
    3. Mention that glucose interpretation depends on fasting status.
    4. Mention that units and laboratory reference ranges must be confirmed.
    5. Do not diagnose diseases.
    6. Do not prescribe medicines or treatments.
    7. Recommend discussing results with a qualified healthcare professional.
    8. Keep the response short and easy to understand.

    Return the response in simple bullet points.
    """

    # PRIMARY PROVIDER: GROQ

    if GROQ_API_KEY:
        try:
            client = Groq(
                api_key=GROQ_API_KEY,
                timeout=20,
                max_retries=0
            )

            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {
                        "role": "system",
                        "content": "You provide general educational health information. Never diagnose diseases."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_completion_tokens=350
            )

            remarks = response.choices[0].message.content

            if remarks and "can't help with that" not in remarks.lower():
                print("AI Provider: Groq")
                return remarks

            print("Groq returned a refusal or empty response.")

        except Exception as e:
            print("Groq API Error:", type(e).__name__, str(e))

    # BACKUP PROVIDER: GEMINI

    if GEMINI_API_KEY:
        try:
            client = genai.Client(
                api_key=GEMINI_API_KEY,
                http_options={"timeout": 15000}
            )

            response = client.interactions.create(
                model="gemini-3.8-flash",
                input=prompt
            )

            remarks = response.output_text

            if remarks and remarks.strip():
                print("AI Provider: Gemini")
                return remarks

            print("Gemini returned an empty response.")

        except Exception as e:
            print("Gemini API Error:", type(e).__name__, str(e))

    # BOTH PROVIDERS FAILED

    return (
        "AI remarks are temporarily unavailable. "
        "Please try again later."
    )
