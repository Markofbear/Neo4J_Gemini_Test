import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=api_key)

model = genai.GenerativeModel("models/gemini-1.5-pro-latest")  # 🔹 Change model ID

def test_gemini():
    response = model.generate_content("Summarize: AI Chatbot - An NLP-powered chatbot that understands user intent.")
    print("🔹 Gemini AI Response:", response.text)

test_gemini()
