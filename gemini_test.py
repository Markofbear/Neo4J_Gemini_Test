import google.generativeai as genai
import os
from dotenv import load_dotenv

# ✅ Load .env file
load_dotenv()

# ✅ Get API Key from environment
api_key = os.getenv("GOOGLE_API_KEY")

# ✅ Configure Gemini AI
genai.configure(api_key=api_key)

# ✅ Use a working Gemini model
model = genai.GenerativeModel("models/gemini-1.5-pro-latest")  # 🔹 Change model ID

# ✅ Test Gemini AI
def test_gemini():
    response = model.generate_content("Summarize: AI Chatbot - An NLP-powered chatbot that understands user intent.")
    print("🔹 Gemini AI Response:", response.text)

test_gemini()
