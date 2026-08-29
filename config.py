import os
import logging
from dotenv import load_dotenv

# Load environment variables (override=True ensures fresh UI saves are loaded)
load_dotenv(override=True)

import sys
# Force UTF-8 encoding for standard output to support emojis in Windows console
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("modawen.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
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
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

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
        LLM_PROVIDER = agent_settings.get("llm_provider", "gemini").lower()
        IMAGE_PROVIDER = agent_settings.get("image_provider", "openai").lower()
        POST_STATUS = agent_settings.get("post_status", "draft").lower()
        
        schedule_settings = yaml_config.get("schedule_settings", {})
        SCHEDULE_ENABLED = schedule_settings.get("enabled", False)
        SCHEDULE_TIME = schedule_settings.get("time", "08:00")
except Exception as e:
    logger.error(f"Failed to load {CONFIG_FILE}: {e}")
    sys.exit(1)

# Ensure API key is set for LangChain
if GEMINI_API_KEY:
    os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY
if OPENAI_API_KEY:
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
if ANTHROPIC_API_KEY:
    os.environ["ANTHROPIC_API_KEY"] = ANTHROPIC_API_KEY

if not GEMINI_API_KEY and not OPENAI_API_KEY and not ANTHROPIC_API_KEY:
    logger.warning("No LLM API keys are set. Agents will fail to run.")
