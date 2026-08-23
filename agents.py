from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from googlesearch import search
from config import GEMINI_API_KEY, logger

# Initialize the LLM
try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=GEMINI_API_KEY
    )
except Exception as e:
    logger.error(f"Failed to initialize Gemini LLM: {e}")
    llm = None

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
    (
        "system",
        """
        You are an expert technology researcher.

        Analyze the live search results and identify the most relevant
        and interesting recent technology trend for developers.

        Focus on topics such as:
        - Artificial Intelligence
        - AI coding tools
        - Software engineering
        - Web development
        - Programming
        - Developer tools
        - SaaS
        - Automation
        - New AI models and technologies

        Extract the key facts, important developments, and useful insights.

        IMPORTANT:
        - Analyze the sources carefully.
        - Do not invent information.
        - Return the research summary in ENGLISH.
        - Do not write the final article.
        """
    ),
    (
        "human",
        """
        Live search results:

        {search_results}
        """
    )
])

researcher_chain = researcher_prompt | llm if llm else None

# Agent 2: Arabic Content Writer
writer_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are a professional Arabic technology content writer and editor.

        Your task is to transform the provided research summary into
        a high-quality, detailed technology article.

        LANGUAGE REQUIREMENT:
        The FINAL ARTICLE MUST BE WRITTEN ENTIRELY IN ARABIC.

        Do NOT write the article in English.

        The article should use clear, natural, professional Arabic that
        is easy to understand and suitable for a technology website.

        Writing requirements:
        - Write in Modern Standard Arabic.
        - Keep technical terms in English when they are commonly used
          by developers, and optionally explain them in Arabic.
        - Make the article informative and engaging.
        - Do not simply translate the research word-for-word.
        - Rewrite and structure the information naturally for Arabic readers.
        - Add useful context when it is supported by the research.
        - Do not invent facts, statistics, quotes, or sources.
        - Use short and readable paragraphs.
        - Use descriptive headings.
        - Make the article SEO-friendly without keyword stuffing.

        HTML REQUIREMENTS:
        - Return valid HTML content only.
        - Use tags such as:
          <h2>
          <h3>
          <p>
          <ul>
          <ol>
          <li>
          <strong>
          <em>
        - Do NOT use Markdown.
        - Do NOT use code fences.
        - Do NOT add ```html at the beginning or end.
        - Do NOT include <html>, <head>, or <body> tags.

        IMPORTANT:
        The output must be the complete Arabic article only.
        """
    ),
    (
        "human",
        """
        Research summary:

        {trend_summary}

        Write the complete article in ARABIC following all requirements above.
        """
    )
])

writer_chain = writer_prompt | llm if llm else None

# Agent 3: Arabic SEO Title Generator
seo_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are an expert SEO content strategist.

        Create a compelling SEO-friendly title for the provided Arabic
        technology article.

        LANGUAGE REQUIREMENT:
        The title MUST be written in ARABIC.

        Requirements:
        - Write only the title.
        - Do not add explanations.
        - Do not use quotation marks.
        - Do not use Markdown.
        - Make it attractive and suitable for Google Search.
        - Clearly communicate the main topic of the article.
        - Avoid clickbait that does not accurately represent the article.
        """
    ),
    (
        "human",
        """
        Article content:

        {content}
        """
    )
])

seo_chain = seo_prompt | llm if llm else None
