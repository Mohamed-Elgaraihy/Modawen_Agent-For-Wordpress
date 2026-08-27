from config import logger, SEARCH_QUERY, NUMBER_OF_ARTICLES, PEXELS_API_KEY, OPENAI_IMAGE_API_KEY
from agents import search_latest_tech_news, researcher_chain, writer_chain, seo_chain, image_query_chain
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

    for i in range(NUMBER_OF_ARTICLES):
        logger.info(f"\n--- Generating Article {i+1} of {NUMBER_OF_ARTICLES} ---")
        
        # Optionally tweak query for multiple articles to get variety
        current_query = f"{SEARCH_QUERY} update {i+1}" if NUMBER_OF_ARTICLES > 1 else SEARCH_QUERY
        
        logger.info(f"🔍 Agent 1 (Researcher): Searching for: '{current_query}'")
        live_data = search_latest_tech_news(current_query)
        
        if not live_data:
            logger.error("No data retrieved from search. Skipping this article.")
            continue

        logger.info("💡 Agent 1: Analyzing search results and extracting the main trend...")
        try:
            trend_summary = researcher_chain.invoke({"search_results": live_data}).content
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

        logger.info("🚀 Publishing the article as a WordPress draft...")
        result = publish_to_wordpress(
            title=article_title, 
            content=article_content, 
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