from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from googlesearch import search
import yaml
import sys
from config import GEMINI_API_KEY, TARGET_LANGUAGE, logger

# Initialize the LLM
try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=GEMINI_API_KEY
    )
except Exception as e:
    logger.error(f"Failed to initialize Gemini LLM: {e}")
    llm = None

# Load Prompts from YAML
PROMPTS_FILE = "prompts.yaml"
try:
    with open(PROMPTS_FILE, "r", encoding="utf-8") as f:
        prompts_config = yaml.safe_load(f)
except Exception as e:
    logger.error(f"Failed to load {PROMPTS_FILE}: {e}")
    sys.exit(1)

def search_latest_tech_news(query: str) -> str:
    """Search Google dynamically for live information related to the given query."""
    results = []
    
    if not llm:
        logger.error("LLM is not initialized. Cannot perform fallback.")
        return ""

    logger.info(f"Performing Google Search for query: '{query}'")
    try:
        # Search Google using the query provided by the AI agent
        search_results = search(
            query,
            num_results=5,
            advanced=True
        )

        for r in search_results:
            results.append(
                f"Title: {r.title}\n"
                f"Summary: {r.description}\n"
                f"URL: {r.url}\n"
            )

        final_text = "\n".join(results)

        if final_text.strip():
            logger.info("Successfully retrieved search results.")
            return final_text

    except Exception as e:
        logger.warning(f"Search error occurred: {e}. Falling back to LLM summary.")

    # If the web search fails, ask the AI model to provide
    # a general summary related to the same topic
    fallback_prompt = (
        f"Provide a general summary of the latest developments "
        f"and trends related to: {query}"
    )

    try:
        fallback_result = llm.invoke(fallback_prompt).content
        return fallback_result
    except Exception as e:
        logger.error(f"Fallback LLM invocation failed: {e}")
        return ""

# ==========================================
# Agent Definitions
# ==========================================

# Agent 1: Technology Researcher
researcher_prompt = ChatPromptTemplate.from_messages([
    ("system", prompts_config.get("researcher", "You are a researcher.")),
    ("human", "Live search results:\n{search_results}")
])
researcher_chain = researcher_prompt | llm if llm else None

# Agent 2: Content Writer
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", prompts_config.get("writer", "You are a writer.").replace("{target_language}", TARGET_LANGUAGE)),
    ("human", "Research summary:\n{trend_summary}\n\nWrite the complete article in {target_language} following all requirements above.".replace("{target_language}", TARGET_LANGUAGE))
])
writer_chain = writer_prompt | llm if llm else None

# Agent 3: Metadata & SEO Agent (Outputs JSON)
seo_prompt = ChatPromptTemplate.from_messages([
    ("system", prompts_config.get("metadata", "You are an SEO expert.").replace("{target_language}", TARGET_LANGUAGE)),
    ("human", "Existing Categories:\n{categories}\n\nArticle content:\n{content}")
])
# We enforce JSON response format if supported by LLM, but for LangChain basic invoke we can just request it in the prompt.
# We will parse the output as JSON in main.py
seo_chain = seo_prompt | llm if llm else None

# Agent 4: Image Search Query Generator
image_query_prompt = ChatPromptTemplate.from_messages([
    ("system", prompts_config.get("image_query", "You are an image researcher.")),
    ("human", "Article context:\n{context}")
])
image_query_chain = image_query_prompt | llm if llm else None

# Agent 5: Topic Generator (Diversification)
topic_generator_prompt = ChatPromptTemplate.from_messages([
    ("system", prompts_config.get("topic_generator", "You are a content strategist.")),
    ("human", "MAIN TOPIC: {search_query}\nNUMBER OF TOPICS TO GENERATE: {number_of_articles}")
])
topic_generator_chain = topic_generator_prompt | llm if llm else None
