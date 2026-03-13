import os
import dotenv
dotenv.load_dotenv()
# Page configuration
PAGE_CONFIG = {
    "page_title": "Document Chat",
    "layout": "wide",
    "initial_sidebar_state": "auto",
}

# App settings
APP_TITLE = "📄 Document Chat with LLM"
INPUT_PLACEHOLDER = "e.g., summarize it, what is..."
INPUT_HEIGHT = 100

# Document handling mode: 'merge' or 'replace'
# Set via environment variable: DOCUMENT_MODE=merge or DOCUMENT_MODE=replace
DOCUMENT_MODE = os.getenv('DOCUMENT_MODE', 'replace').lower()
if DOCUMENT_MODE not in ['merge', 'replace']:
    DOCUMENT_MODE = 'merge'
