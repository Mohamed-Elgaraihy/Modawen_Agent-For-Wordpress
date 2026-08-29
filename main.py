from config import logger, SEARCH_QUERY, NUMBER_OF_ARTICLES, PEXELS_API_KEY, OPENAI_IMAGE_API_KEY
from agents import search_latest_tech_news, researcher_chain, writer_chain, seo_chain, image_query_chain, topic_generator_chain
from utils import publish_to_wordpress, get_pexels_image_url, upload_image_to_wordpress, get_openai_image_url, get_wp_categories, create_wp_category, create_wp_tags
import json

def run_agent_pipeline():
    """Run the complete Modawen agent pipeline."""
    if not researcher_chain or not writer_chain or not seo_chain:
        logger.error("Agents are not initialized correctly. Please check your GEMINI_API_KEY.")
        return

    logger.info(f"Starting pipeline to generate {NUMBER_OF_ARTICLES} article(s)...")

    # Fetch existing categories once
    existing_categories = get_wp_categories()
    categories_text = json.dumps(existing_categories, ensure_ascii=False) if existing_categories else "No existing categories found."

    # Always generate a pool of distinct sub-topics for variety
    topic_list = []
    if topic_generator_chain:
        logger.info(f"🧠 Agent 5 (Topic Generator): Creating a pool of distinct sub-topics for '{SEARCH_QUERY}'...")
        try:
            # We always ask for a larger pool (e.g., 10) to ensure randomness across manual runs
            pool_size = max(10, NUMBER_OF_ARTICLES * 2)
            topic_response = topic_generator_chain.invoke({
                "search_query": SEARCH_QUERY, 
                "number_of_articles": pool_size
            }).content
            topic_clean = topic_response.strip().removeprefix("```json").removesuffix("```").strip()
            topic_list = json.loads(topic_clean)
            
            if not isinstance(topic_list, list) or len(topic_list) == 0:
                raise ValueError("Topic generator did not return a valid list.")
                
            import random
            # Randomly select the exact number of articles requested to guarantee variety across manual runs
            topic_list = random.sample(topic_list, min(NUMBER_OF_ARTICLES, len(topic_list)))
            
            # If the user asked for more articles than the pool returned, we pad the list
            while len(topic_list) < NUMBER_OF_ARTICLES:
                topic_list.append(f"{SEARCH_QUERY} update {len(topic_list)+1}")
                
            logger.info(f"✨ Selected unique topics for this run: {topic_list}")
        except Exception as e:
            logger.error(f"Topic Generator failed: {e}. Falling back to default query logic.")
            topic_list = [f"{SEARCH_QUERY} update {i+1}" for i in range(NUMBER_OF_ARTICLES)]
    else:
        topic_list = [f"{SEARCH_QUERY} update {i+1}" for i in range(NUMBER_OF_ARTICLES)]

    for i in range(NUMBER_OF_ARTICLES):
        logger.info(f"\n--- Generating Article {i+1} of {NUMBER_OF_ARTICLES} ---")
        
        # Get the specific query for this iteration
        current_query = topic_list[i] if i < len(topic_list) else f"{SEARCH_QUERY} update {i+1}"
        
        logger.info(f"🔍 Agent 1 (Researcher): Searching for: '{current_query}'")
        live_data = search_latest_tech_news(current_query)
        
        if not live_data:
            logger.error("No data retrieved from search. Skipping this article.")
            continue

        logger.info("💡 Agent 1: Analyzing search results and extracting the main trend...")
        try:
            trend_summary = researcher_chain.invoke({"search_results": live_data}).content
            # FORCE the URLs into the summary so the writer agent absolutely uses them
            trend_summary += "\n\nRAW SOURCE URLS FOR LINKING (YOU MUST USE THESE):\n" + live_data
        except Exception as e:
            logger.error(f"Researcher agent failed: {e}")
            continue

        logger.info("🤖 Agent 2 (Writer): Writing the Arabic article...")
        try:
            article_content = writer_chain.invoke({"trend_summary": trend_summary}).content
        except Exception as e:
            logger.error(f"Writer agent failed: {e}")
            continue

        logger.info("🤖 Agent 3 (Metadata & SEO): Generating JSON metadata...")
        try:
            seo_output = seo_chain.invoke({
                "categories": categories_text, 
                "content": article_content
            }).content
            
            # Clean JSON output from potential markdown formatting
            seo_output_clean = seo_output.strip().removeprefix("```json").removesuffix("```").strip()
            metadata = json.loads(seo_output_clean)
            
            article_title = metadata.get("title", "Generated Article")
            tags = metadata.get("tags", [])
            category_id = metadata.get("category_id")
            new_category_name = metadata.get("new_category_name")
            
        except Exception as e:
            logger.error(f"SEO agent or JSON parsing failed: {e}. Fallback to basic title.")
            article_title = f"Article {i+1}"
            tags = []
            category_id = None
            new_category_name = None

        # Resolve Category
        category_ids = []
        if category_id:
            category_ids.append(category_id)
        elif new_category_name:
            logger.info(f"Creating new category: '{new_category_name}'")
            new_id = create_wp_category(new_category_name)
            if new_id:
                category_ids.append(new_id)

        # Resolve Tags
        tag_ids = []
        if tags:
            logger.info(f"Creating/fetching tags: {tags}")
            tag_ids = create_wp_tags(tags)

        logger.info("🖼️ Agent 4 (Image Selection): Resolving image API strategy...")
        featured_media_id = None
        image_url = None
        image_query = "technology"

        # Determine which API to use
        use_pexels = bool(PEXELS_API_KEY)
        use_openai = bool(OPENAI_IMAGE_API_KEY)
        selected_api = None

        if use_pexels and use_openai:
            from config import IMAGE_PROVIDER
            if IMAGE_PROVIDER == 'pexels':
                selected_api = "pexels"
                logger.info("Using Pexels for Featured Image (configured in Settings).")
            else:
                selected_api = "openai"
                logger.info("Using OpenAI for Featured Image (configured in Settings).")
        elif use_pexels:
            selected_api = "pexels"
        elif use_openai:
            selected_api = "openai"
        else:
            logger.warning("No image APIs configured in .env. Skipping featured image generation.")

        # Execute Image Fetching if an API was selected
        if selected_api and image_query_chain:
            try:
                image_query = image_query_chain.invoke({"context": trend_summary}).content
                logger.info(f"Generated Image Query: {image_query}")
                
                if selected_api == "pexels":
                    image_url = get_pexels_image_url(image_query)
                elif selected_api == "openai":
                    dalle_prompt = f"A high-quality, professional editorial illustration about: {image_query}. No text in image."
                    image_url = get_openai_image_url(dalle_prompt)

                if image_url:
                    featured_media_id = upload_image_to_wordpress(image_url, image_query)
            except Exception as e:
                logger.error(f"Image fetching failed: {e}")
        elif selected_api:
            logger.warning("Image Query Agent not initialized. Cannot fetch image.")

        from config import POST_STATUS
        logger.info(f"🚀 Pushing the article to WordPress as '{POST_STATUS}'...")
        result = publish_to_wordpress(
            title=article_title, 
            content=article_content, 
            status=POST_STATUS,
            featured_media_id=featured_media_id,
            category_ids=category_ids,
            tag_ids=tag_ids
        )
        
        logger.info(f"✅ Final result for Article {i+1}: {result}")
        print(f"\n✅ Final result: {result}")

if __name__ == "__main__":
    logger.info("Starting Modawen Agent Pipeline...")
    run_agent_pipeline()
    logger.info("Pipeline execution completed.")