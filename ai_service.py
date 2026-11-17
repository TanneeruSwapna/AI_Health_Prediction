
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")


def generate_health_remarks(glucose, haemoglobin, cholesterol):

    if not API_KEY:
        return "AI remarks unavailable: Gemini API key is missing."

    try:
        client = genai.Client(
            api_key=API_KEY,
            http_options={"timeout": 120000}
        )

        prompt = f"""
        You are a health information assistant.

        Patient readings:
        Glucose: {glucose}
        Haemoglobin: {haemoglobin}
        Cholesterol: {cholesterol}

        Explain each reading in simple language.
        Mention that interpretation depends on units,
        fasting status and laboratory reference ranges.
        Do not provide a medical diagnosis.
        Recommend consulting a healthcare professional.
        """

        response = client.interactions.create(
            model="gemini-3.8-flash",
            input=prompt
        )

        return response.output_text or "AI remarks could not be generated."

    except Exception as e:
        print("Gemini API Error:", str(e))
        return "AI remarks are temporarily unavailable. Please try again later."


