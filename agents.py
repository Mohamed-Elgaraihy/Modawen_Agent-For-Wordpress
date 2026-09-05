from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from googlesearch import search
import yaml
import sys
from config import GEMINI_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY, TARGET_LANGUAGE, LLM_PROVIDER, logger

# Initialize the LLM dynamically based on configuration
try:
    if LLM_PROVIDER == "openai":
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set.")
        llm = ChatOpenAI(model="gpt-4o", openai_api_key=OPENAI_API_KEY)
        logger.info("Successfully initialized OpenAI (GPT-4o) LLM.")
    elif LLM_PROVIDER == "anthropic":
        if not ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is not set.")
        llm = ChatAnthropic(model="claude-3-5-sonnet-20240620", anthropic_api_key=ANTHROPIC_API_KEY)
        logger.info("Successfully initialized Anthropic (Claude 3.5) LLM.")
    else:
        # Default to Gemini
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set.")
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=GEMINI_API_KEY)
        logger.info("Successfully initialized Google Gemini LLM.")
except Exception as e:
    logger.error(f"Failed to initialize LLM '{LLM_PROVIDER}': {e}")
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
import datetime
CURRENT_YEAR = datetime.datetime.now().year
YEAR_INSTRUCTION = f"\n\nCRITICAL CONTEXT: The current year is {CURRENT_YEAR}. Ensure your knowledge is up to date and do NOT write about outdated trends from 2023 or 2024. IMPORTANT: Do NOT forcefully hardcode '{CURRENT_YEAR}' into every topic or paragraph. Keep the writing natural and evergreen."

# Agent 1: Technology Researcher
researcher_prompt = ChatPromptTemplate.from_messages([
    ("system", prompts_config.get("researcher", "You are a researcher.") + YEAR_INSTRUCTION),
    ("human", "Live search results:\n{search_results}")
])
researcher_chain = researcher_prompt | llm if llm else None

# Agent 2: Content Writer
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", prompts_config.get("writer", "You are a writer.").replace("{target_language}", TARGET_LANGUAGE) + YEAR_INSTRUCTION + "\n\nCRITICAL AI RULE: Do NOT output any internal notes, disclaimers, or meta-commentary (e.g. 'Note:'). Output ONLY the final article text. If no external source URLs are provided, do NOT invent dummy URLs (e.g. example.com)."),
    ("human", "Research summary:\n{trend_summary}\n\nInternal Links Available:\n{internal_links}\n\nWrite the complete article in {target_language}. You MUST organically embed 1-2 <a> tags linking to the 'Internal Links Available'. If specific 'RAW SOURCE URLS' are provided, you MUST also naturally embed them as external <a> tags.".replace("{target_language}", TARGET_LANGUAGE))
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

# Agent 5: Topic Generator
topic_generator_prompt = ChatPromptTemplate.from_messages([
    ("system", prompts_config.get("topic_generator", "You are a trend analyzer.").replace("{target_language}", TARGET_LANGUAGE) + YEAR_INSTRUCTION),
    ("human", "Generate a JSON list of exactly {number_of_articles} highly specific, viral sub-topics or unique angles related to the broad topic: '{search_query}'. The topics MUST be in {target_language}. Output ONLY a raw JSON array of strings.".replace("{target_language}", TARGET_LANGUAGE))
])
topic_generator_chain = topic_generator_prompt | llm if llm else None

# Agent 6: Social Media Manager (Twitter/X Thread)
social_prompt = ChatPromptTemplate.from_messages([
    ("system", prompts_config.get("social", "You are a viral Social Media Manager. Your job is to read a long-form article and write a highly engaging, viral Twitter (X) thread summarizing the key points to drive traffic to the blog.").replace("{target_language}", TARGET_LANGUAGE) + YEAR_INSTRUCTION + "\n\nCRITICAL AI RULE: Write the thread naturally, use emojis, include relevant hashtags, and end with a call to action linking to the full article. Do NOT write any internal notes or disclaimers."),
    ("human", "Article Title:\n{title}\n\nArticle Content:\n{content}\n\nWrite a 3-5 tweet viral thread in {target_language} based on this article.".replace("{target_language}", TARGET_LANGUAGE))
])
social_chain = social_prompt | llm if llm else None
