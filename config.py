import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Central configuration for the AI Software Engineering Assistant."""

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    MODEL_NAME = "openai/gpt-oss-120b"
    MODEL_TEMPERATURE = 0.2

    MAX_CODE_LENGTH = 8000  # rough char limit to stay within token budget

    RETRY_MIN_WAIT = 4
    RETRY_MAX_WAIT = 30
    RETRY_MAX_ATTEMPTS = 5

    APP_TITLE = "🛠️ AI Software Engineering Assistant"
    APP_CAPTION = "Paste your code and get an automated review: analysis, bug detection, generated tests, and a code health score."
    PAGE_TITLE = "AI Software Engineering Assistant"

    SUPPORTED_LANGUAGES = ["Python", "JavaScript", "Java", "C++", "TypeScript", "Go", "Other"]