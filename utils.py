import re
import requests
import tempfile
import os
from requests.auth import HTTPBasicAuth
from config import WP_URL, WP_USERNAME, WP_APP_PASSWORD, PEXELS_API_KEY, logger

def clean_html_content(raw_html: str) -> str:
    """Remove unnecessary Markdown code fences from generated HTML."""
    try:
        clean_text = re.sub(r"^```html\s*", "", raw_html, flags=re.MULTILINE)
        clean_text = re.sub(r"^```\s*", "", clean_text, flags=re.MULTILINE)
        return clean_text.strip()
    except Exception as e:
        logger.error(f"Error cleaning HTML content: {e}")
        return raw_html

def get_pexels_image_url(query: str) -> str:
    """Search Pexels for an image and return its URL."""
    if not PEXELS_API_KEY:
        logger.warning("PEXELS_API_KEY is not set. Skipping image search.")
        return None

    logger.info(f"Searching Pexels for image related to: '{query}'")
    headers = {"Authorization": PEXELS_API_KEY}
    url = f"https://api.pexels.com/v1/search?query={query}&per_page=1"
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        if data.get("photos") and len(data["photos"]) > 0:
            image_url = data["photos"][0]["src"]["large"]
            logger.info(f"Found Pexels image: {image_url}")
            return image_url
        else:
            logger.warning(f"No images found on Pexels for query: '{query}'")
    except requests.exceptions.RequestException as e:
        logger.error(f"Pexels API request failed: {e}")
    return None

def get_openai_image_url(prompt: str) -> str:
    """Generate an image using OpenAI DALL-E 3 and return its URL."""
    from config import OPENAI_IMAGE_API_KEY
    if not OPENAI_IMAGE_API_KEY:
        logger.warning("OPENAI_IMAGE_API_KEY is not set. Skipping OpenAI image generation.")
        return None

    logger.info(f"Generating image via OpenAI for prompt: '{prompt}'")
    headers = {
        "Authorization": f"Bearer {OPENAI_IMAGE_API_KEY}",
        "Content-Type": "application/json"
    }
    url = "https://api.openai.com/v1/images/generations"
    payload = {
        "model": "gpt-image-2",
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        
        if data.get("data") and len(data["data"]) > 0:
            image_item = data["data"][0]
            if "url" in image_item:
                image_url = image_item["url"]
                logger.info("Successfully generated image with OpenAI (URL format).")
                return image_url
            elif "b64_json" in image_item:
                logger.info("Successfully generated image with OpenAI (Base64 format).")
                return "b64:" + image_item["b64_json"]
            else:
                logger.error(f"OpenAI response missing 'url' and 'b64_json' keys. Raw data: {data}")
        else:
            logger.warning(f"OpenAI API returned success but no image data was found. Raw data: {data}")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"OpenAI API request failed: {e}")
        if e.response is not None:
            logger.error(f"Response details: {e.response.text}")
    except Exception as e:
        logger.error(f"Unexpected error processing OpenAI response: {e}")
        
    return None


def upload_image_to_wordpress(image_url: str, title: str) -> int:
    """Download an image from URL and upload it to WordPress Media Library."""
    if not WP_URL or not WP_USERNAME or not WP_APP_PASSWORD:
        return None

    try:
        import base64
        # Create temporary file
        fd, temp_path = tempfile.mkstemp(suffix=".jpg")
        
        with os.fdopen(fd, 'wb') as f:
            if image_url.startswith("b64:"):
                logger.info("Decoding Base64 image data...")
                b64_data = image_url.replace("b64:", "", 1)
                f.write(base64.b64decode(b64_data))
            else:
                logger.info(f"Downloading image from {image_url}...")
                img_response = requests.get(image_url, timeout=30)
                img_response.raise_for_status()
                f.write(img_response.content)

        # Upload to WordPress
        logger.info("Uploading image to WordPress Media Library...")
        media_url = f"{WP_URL.rstrip('/')}/wp-json/wp/v2/media"
        
        # Clean title for filename
        clean_name = re.sub(r'[^a-zA-Z0-9_-]', '_', title[:30]) + ".jpg"

        with open(temp_path, 'rb') as f:
            headers = {
                'Content-Disposition': f'attachment; filename="{clean_name}"',
                'Content-Type': 'image/jpeg'
            }
            media_response = requests.post(
                media_url,
                headers=headers,
                data=f,
                auth=HTTPBasicAuth(WP_USERNAME, WP_APP_PASSWORD),
                timeout=60
            )
        
        # Clean up temp file
        os.remove(temp_path)

        media_response.raise_for_status()
        media_id = media_response.json().get('id')
        logger.info(f"Successfully uploaded media. ID: {media_id}")
        return media_id

    except Exception as e:
        logger.error(f"Failed to upload image to WordPress: {e}")
        return None

def get_wp_categories() -> list:
    """Fetch existing categories from WordPress."""
    if not WP_URL or not WP_USERNAME or not WP_APP_PASSWORD:
        return []
    
    api_url = f"{WP_URL.rstrip('/')}/wp-json/wp/v2/categories?per_page=100"
    try:
        response = requests.get(
            api_url,
            auth=HTTPBasicAuth(WP_USERNAME, WP_APP_PASSWORD),
            timeout=15
        )
        response.raise_for_status()
        categories = response.json()
        return [{"id": cat["id"], "name": cat["name"]} for cat in categories]
    except Exception as e:
        logger.error(f"Failed to fetch WordPress categories: {e}")
        return []

def create_wp_category(name: str) -> int:
    """Create a new category in WordPress and return its ID."""
    if not WP_URL or not WP_USERNAME or not WP_APP_PASSWORD:
        return None
        
    api_url = f"{WP_URL.rstrip('/')}/wp-json/wp/v2/categories"
    payload = {"name": name}
    try:
        response = requests.post(
            api_url,
            json=payload,
            auth=HTTPBasicAuth(WP_USERNAME, WP_APP_PASSWORD),
            timeout=15
        )
        # 400 status often means term already exists
        if response.status_code == 400 and 'term_exists' in response.text:
            logger.info(f"Category '{name}' already exists.")
            return response.json().get('data', {}).get('term_id')
            
        response.raise_for_status()
        return response.json().get('id')
    except Exception as e:
        logger.error(f"Failed to create WordPress category '{name}': {e}")
        return None

def create_wp_tags(tags: list) -> list:
    """Create new tags in WordPress and return their IDs."""
    if not WP_URL or not WP_USERNAME or not WP_APP_PASSWORD or not tags:
        return []
        
    api_url = f"{WP_URL.rstrip('/')}/wp-json/wp/v2/tags"
    tag_ids = []
    
    for tag_name in tags:
        payload = {"name": tag_name}
        try:
            response = requests.post(
                api_url,
                json=payload,
                auth=HTTPBasicAuth(WP_USERNAME, WP_APP_PASSWORD),
                timeout=15
            )
            if response.status_code == 400 and 'term_exists' in response.text:
                tag_id = response.json().get('data', {}).get('term_id')
                tag_ids.append(tag_id)
            else:
                response.raise_for_status()
                tag_ids.append(response.json().get('id'))
        except Exception as e:
            logger.error(f"Failed to create WordPress tag '{tag_name}': {e}")
            
    return tag_ids

def publish_to_wordpress(title: str, content: str, status: str = "draft", featured_media_id: int = None, category_ids: list = None, tag_ids: list = None) -> str:
    """Create a WordPress post with an optional featured image, categories, and tags."""
    if not WP_URL or not WP_USERNAME or not WP_APP_PASSWORD:
        logger.error("WordPress credentials are not fully configured in .env.")
        return "Failed: WordPress credentials missing."

    api_url = f"{WP_URL.rstrip('/')}/wp-json/wp/v2/posts"
    
    # Clean generated content and title before publishing
    clean_content = clean_html_content(content)
    clean_title = clean_html_content(title).replace('"', '')

    payload = {
        "title": clean_title,
        "content": clean_content,
        "status": status
    }
    
    if featured_media_id:
        payload["featured_media"] = featured_media_id
    if category_ids:
        payload["categories"] = category_ids
    if tag_ids:
        payload["tags"] = tag_ids

    try:
        response = requests.post(
            api_url,
            json=payload,
            auth=HTTPBasicAuth(WP_USERNAME, WP_APP_PASSWORD),
            timeout=30
        )
        response.raise_for_status()
        
        post_id = response.json().get('id')
        logger.info(f"Successfully created WordPress post with ID: {post_id}")
        return f"Success! Created post with ID: {post_id}"
        
    except requests.exceptions.RequestException as e:
        logger.error(f"WordPress API request failed: {e}")
        if e.response is not None:
            logger.error(f"Response details: {e.response.text}")
        return f"Failed to publish to WordPress: {e}"

