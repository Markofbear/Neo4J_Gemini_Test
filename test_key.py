import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load API key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("API Key not loaded correctly.")
else:
    genai.configure(api_key=api_key)
    print("API Key is valid, configuration successful.")