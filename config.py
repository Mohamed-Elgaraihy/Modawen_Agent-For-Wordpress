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

# Configuration from YAML
import yaml
import sys

CONFIG_FILE = "config.yaml"
try:
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        yaml_config = yaml.safe_load(f)
        agent_settings = yaml_config.get("agent_settings", {})
        SEARCH_QUERY = agent_settings.get("search_query", "latest AI software engineering trends news")
        TARGET_LANGUAGE = agent_settings.get("target_language", "Arabic")
        NUMBER_OF_ARTICLES = agent_settings.get("number_of_articles", 1)
except Exception as e:
    logger.error(f"Failed to load {CONFIG_FILE}: {e}")
    sys.exit(1)

# Ensure API key is set for LangChain
if GEMINI_API_KEY:
    os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY
else:
    logger.warning("GEMINI_API_KEY is not set. Agents will fail to run.")
