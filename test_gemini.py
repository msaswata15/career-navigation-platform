import os
import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv("backend/.env")

async def test_gemini():
    api_key = os.getenv("GOOGLE_API_KEY")
    print(f"API Key found: {bool(api_key)}")
    
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key
        )
        print("LLM initialized. Invoking...")
        response = await llm.ainvoke("Hello, are you working?")
        print(f"Response: {response.content}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_gemini())
