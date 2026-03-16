import json
import logging
import google.generativeai as genai
from app.config.settings import settings
from app.utils.parser import format_prompt

logger = logging.getLogger(__name__)

# Configure Gemini AI
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

class AIService:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-flash') if settings.GEMINI_API_KEY else None

    async def analyze_code(self, code: str) -> dict:
        if not self.model:
            logger.warning("Gemini API key not configured. Returning mock response.")
            return self._mock_response()
            
        prompt = format_prompt(code)
        
        try:
            response = await self.model.generate_content_async(prompt)
            # Find the JSON block inside the response text, which handles cases where there is extra dialogue
            import re
            text = response.text
            match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
            if match:
                cleaned_text = match.group(1)
            else:
                # If no markdown block is found, take the whole text and strip brackets
                cleaned_text = text.strip()
                if cleaned_text.startswith("```"):
                   cleaned_text = cleaned_text.strip("```").strip()

            return json.loads(cleaned_text)
        except Exception as e:
            logger.error(f"AI Analysis error: {e}")
            return self._fallback_response()
            
    def _mock_response(self) -> dict:
        return {
            "issues": [
                {
                    "line_number": 1,
                    "severity": "low",
                    "type": "quality",
                    "description": "Mock issue because API is not configured",
                    "suggestion": "Configure GEMINI_API_KEY in .env"
                }
            ],
            "score": 5.0
        }

    def _fallback_response(self) -> dict:
        return {
            "issues": [
                {
                    "line_number": None,
                    "severity": "critical",
                    "type": "error",
                    "description": "Failed to parse AI response",
                    "suggestion": "Check backend logs for AI service failure."
                }
            ],
            "score": 0.0
        }

ai_service = AIService()
