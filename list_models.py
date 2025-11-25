import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv("backend/.env")

def list_models():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("No API key found")
        return

    genai.configure(api_key=api_key)
    
    print("Listing available models...")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(m.name)
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    list_models()
