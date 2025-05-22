import os
from dotenv import load_dotenv
from uuid import UUID

# Determine project root to correctly locate .env
# This assumes config.py is either in the project root or in a subdirectory like src/
# If config.py is in src/, (os.path.dirname(__file__), "..") goes to project root
# If config.py is in project root, (os.path.dirname(__file__)) IS project root
current_script_path = os.path.dirname(__file__)
# Heuristic: if 'src' is in the path, go one level up from 'src'. Otherwise, assume current dir is root.
if 'src' in current_script_path.split(os.sep)[-2:]: # Checks if 'src' is parent or grandparent
    project_root = os.path.abspath(os.path.join(current_script_path, ".."))
else:
    project_root = os.path.abspath(current_script_path)

dotenv_path = os.path.join(project_root, '.env')

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    print(f"Config: Loaded .env file from: {dotenv_path}")
else:
    print(f"Config: Warning: .env file not found at {dotenv_path}. API key might not be loaded.")

class AppConfig: # Renamed to avoid conflict with your RAG system's Config class
    """
    Configuration settings for the Streamlit Chatbot application.
    """
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "YOUR_GOOGLE_API_KEY_FALLBACK")
    
    # Model configuration for the chatbot
    # You might have different models for chat vs. image analysis vs. RAG tasks
    CHATBOT_MODEL_NAME: str = os.getenv("MODEL_NAME", "gemini-2.5-flash-preview-04-17")
    IMAGE_ANALYSIS_MODEL_NAME: str = os.getenv("MODEL_NAME", "gemini-2.5-flash-preview-04-17") # Often a more powerful model for this

    HISTORY_DIR: str = os.path.join(project_root, "conversation_history")

    def __init__(self):
        if not self.GOOGLE_API_KEY or "FALLBACK" in self.GOOGLE_API_KEY:
            print("Config: WARNING - GOOGLE_API_KEY is not set correctly in .env or is using a placeholder.")
        
        os.makedirs(self.HISTORY_DIR, exist_ok=True)

def load_app_config() -> AppConfig: # Renamed function
    """Load and return configuration settings for the Streamlit app."""
    return AppConfig()

# Example of how to use it if you run this file (optional)
if __name__ == "__main__":
    cfg = load_app_config()
    print(f"API Key Loaded: {'Yes' if cfg.GOOGLE_API_KEY and 'FALLBACK' not in cfg.GOOGLE_API_KEY else 'No/Placeholder'}")
    print(f"Chatbot Model: {cfg.MODEL_NAME}")
    print(f"Image Analysis Model: {cfg.MODEL_NAME}")
    print(f"History Directory: {cfg.HISTORY_DIR}")