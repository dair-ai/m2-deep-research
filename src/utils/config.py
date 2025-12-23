"""Configuration management for Deep Research Agent."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for managing API keys and settings."""

    # Minimax API Configuration
    MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY")
    MINIMAX_BASE_URL = "https://api.minimax.io/anthropic"
    MINIMAX_MODEL = "MiniMax-M2.1"

    # OpenRouter API Configuration
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL = "google/gemini-2.5-flash"

    # Exa API Configuration
    EXA_API_KEY = os.getenv("EXA_API_KEY")
    EXA_BASE_URL = "https://api.exa.ai"

    @classmethod
    def validate(cls):
        """Validate that all required API keys are set."""
        missing = []

        if not cls.MINIMAX_API_KEY:
            missing.append("MINIMAX_API_KEY")
        if not cls.OPENROUTER_API_KEY:
            missing.append("OPENROUTER_API_KEY")
        if not cls.EXA_API_KEY:
            missing.append("EXA_API_KEY")

        if missing:
            raise ValueError(
                f"Missing required API keys: {', '.join(missing)}. "
                f"Please set them in your .env file."
            )

        return True


# Validate configuration on import
try:
    Config.validate()
except ValueError as e:
    print(f"Configuration Error: {e}")
    print("Please copy .env.example to .env and fill in your API keys.")
