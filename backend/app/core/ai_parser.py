"""
AI-powered resume parser using Google Gemini via the official client.
"""

import asyncio

import google.generativeai as genai
from langchain.output_parsers import PydanticOutputParser
from app.models.user import ParsedResume
from app.utils.pdf_parser import extract_text

class AIResumeParser:
    def __init__(self, google_api_key: str):
        genai.configure(api_key=google_api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")
        self.parser = PydanticOutputParser(pydantic_object=ParsedResume)

    async def parse_resume(self, resume_text: str) -> ParsedResume:
        """Parse resume text into a structured format using Gemini."""

        format_instructions = self.parser.get_format_instructions()
        prompt = (
            "You are an expert resume parser. Extract structured information from resumes "
            "accurately. For skills, categorize them and estimate proficiency based on context "
            "(junior/senior role, years of experience mentioned).\n\n"
            f"{format_instructions}\n\n"
            "Resume text:\n\n"
            f"{resume_text}"
        )

        response = await asyncio.to_thread(self.model.generate_content, prompt)
        output_text = getattr(response, "text", None)

        if not output_text:
            raise ValueError("Gemini returned an empty response while parsing resume")

        return self.parser.parse(output_text)

# Usage Example
async def parse_uploaded_resume(file_bytes: bytes, filename: str):
    parser = AIResumeParser(google_api_key="your-key")
    
    # Extract text
    text = extract_text(file_bytes, filename)
    
    # Parse with AI
    parsed_data = await parser.parse_resume(text)
    
    return parsed_data
