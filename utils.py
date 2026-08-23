import re
import requests
from requests.auth import HTTPBasicAuth
from config import WP_URL, WP_USERNAME, WP_APP_PASSWORD, logger

def clean_html_content(raw_html: str) -> str:
    """Remove unnecessary Markdown code fences from generated HTML."""
    try:
        clean_text = re.sub(r"^```html\s*", "", raw_html, flags=re.MULTILINE)
        clean_text = re.sub(r"^```\s*", "", clean_text, flags=re.MULTILINE)
        return clean_text.strip()
    except Exception as e:
        logger.error(f"Error cleaning HTML content: {e}")
        return raw_html

def publish_to_wordpress(title: str, content: str, status: str = "draft") -> str:
    """Create a WordPress post."""
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
