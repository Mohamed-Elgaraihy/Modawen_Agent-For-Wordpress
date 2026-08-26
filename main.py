from config import logger, DEFAULT_TOPIC, PEXELS_API_KEY, OPENAI_IMAGE_API_KEY
from agents import search_latest_tech_news, researcher_chain, writer_chain, seo_chain, image_query_chain
from utils import publish_to_wordpress, get_pexels_image_url, upload_image_to_wordpress, get_openai_image_url

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

    logger.info("🖼️ Agent 4 (Image Selection): Resolving image API strategy...")
    featured_media_id = None
    image_url = None
    image_query = "technology"

    # Determine which API to use
    use_pexels = bool(PEXELS_API_KEY)
    use_openai = bool(OPENAI_IMAGE_API_KEY)
    selected_api = None

    if use_pexels and use_openai:
        print("\n✨ Both Pexels and OpenAI APIs are available for Featured Images.")
        while True:
            choice = input("Which one do you want to use? (Type '1' for Pexels, '2' for OpenAI): ").strip()
            if choice == '1':
                selected_api = "pexels"
                break
            elif choice == '2':
                selected_api = "openai"
                break
            else:
                print("Invalid choice. Please enter 1 or 2.")
    elif use_pexels:
        selected_api = "pexels"
    elif use_openai:
        selected_api = "openai"
    else:
        logger.warning("No image APIs configured in .env (PEXELS_API_KEY or OPENAI_IMAGE_API_KEY). Skipping featured image generation.")
        print("\n⚠️ No image APIs found. The article will be published without a featured image.")

    # Execute Image Fetching if an API was selected
    if selected_api and image_query_chain:
        try:
            image_query = image_query_chain.invoke({"context": trend_summary}).content
            logger.info(f"Generated Image Query: {image_query}")
            
            if selected_api == "pexels":
                image_url = get_pexels_image_url(image_query)
            elif selected_api == "openai":
                # For DALL-E, we can use a slightly richer prompt based on the short query
                dalle_prompt = f"A high-quality, professional editorial illustration about: {image_query}. Tech blog style, no text in image."
                image_url = get_openai_image_url(dalle_prompt)

            if image_url:
                featured_media_id = upload_image_to_wordpress(image_url, image_query)
        except Exception as e:
            logger.error(f"Image fetching failed: {e}")
            print(f"\n⚠️ Image generation/upload failed ({e}). Continuing without image.")
    elif selected_api:
        logger.warning("Image Query Agent not initialized. Cannot fetch image.")

    logger.info("🚀 Publishing the article as a WordPress draft...")
    result = publish_to_wordpress(article_title, article_content, featured_media_id=featured_media_id)
    
    logger.info(f"✅ Final result: {result}")
    print(f"\n✅ Final result: {result}")

if __name__ == "__main__":
    logger.info("Starting Modawen Agent Pipeline...")
    run_agent_pipeline()
    logger.info("Pipeline execution completed.")