import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("modawen.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Modawen")

# Credentials
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WP_URL = os.getenv("WP_URL")
WP_USERNAME = os.getenv("WP_USERNAME")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
OPENAI_IMAGE_API_KEY = os.getenv("OPENAI_IMAGE_API_KEY")



# Default settings
DEFAULT_TOPIC = "latest AI software engineering trends news"

# Ensure API key is set for LangChain
if GEMINI_API_KEY:
    os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY
else:
    logger.warning("GEMINI_API_KEY is not set. Agents will fail to run.")
