from config import logger, DEFAULT_TOPIC
from agents import search_latest_tech_news, researcher_chain, writer_chain, seo_chain
from utils import publish_to_wordpress

def run_agent_pipeline():
    """Run the complete Modawen agent pipeline."""
    if not researcher_chain or not writer_chain or not seo_chain:
        logger.error("Agents are not initialized correctly. Please check your GEMINI_API_KEY.")
        return

    logger.info("🔍 Agent 1 (Researcher): Searching for the latest technology trends...")
    live_data = search_latest_tech_news(DEFAULT_TOPIC)
    
    if not live_data:
        logger.error("No data retrieved from search or fallback. Exiting pipeline.")
        return

    logger.info("💡 Agent 1: Analyzing search results and extracting the main trend...")
    try:
        trend_summary = researcher_chain.invoke({"search_results": live_data}).content
    except Exception as e:
        logger.error(f"Researcher agent failed: {e}")
        return

    logger.info("🤖 Agent 2 (Writer): Writing the Arabic article...")
    try:
        article_content = writer_chain.invoke({"trend_summary": trend_summary}).content
    except Exception as e:
        logger.error(f"Writer agent failed: {e}")
        return

    logger.info("🤖 Agent 3 (SEO Expert): Generating the Arabic SEO title...")
    try:
        article_title = seo_chain.invoke({"content": article_content}).content
    except Exception as e:
        logger.error(f"SEO agent failed: {e}")
        return

    logger.info("🚀 Publishing the article as a WordPress draft...")
    result = publish_to_wordpress(article_title, article_content)
    
    logger.info(f"✅ Final result: {result}")
    print(f"\n✅ Final result: {result}")

if __name__ == "__main__":
    logger.info("Starting Modawen Agent Pipeline...")
    run_agent_pipeline()
    logger.info("Pipeline execution completed.")