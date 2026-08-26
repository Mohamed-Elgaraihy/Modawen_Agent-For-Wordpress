# Modawen Agent for WordPress

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)

**Modawen Agent for WordPress** is an open-source, AI-powered multi-agent system that researches live trends, writes high-quality articles, generates featured images (via DALL-E 3 or Pexels), intelligently manages SEO metadata, and publishes automatically to WordPress.

Created by **Mohamed Elgaraihy** ([@EngMoElgaraihy on X](https://x.com/EngMoElgaraihy)).

## 🌟 Features

- **Live Research:** Uses Google Search dynamically to gather the latest news and avoid AI hallucinations.
- **Multi-Agent System:**
  - 🔍 **Technology Researcher Agent:** Analyzes live search results to extract key insights and facts.
  - ✍️ **Content Writer Agent:** Transforms the research into a natural, SEO-friendly, and professional article in your chosen language.
  - 🎯 **Metadata & SEO Agent:** Generates an attractive title, creates SEO tags, and intelligently selects the best existing WordPress Category (or creates a new one).
  - 🖼️ **Image Query Agent:** Generates an English query to find the perfect stock photo or AI image.
- **Dynamic Configuration:** Easily change search topics, target languages, and run loops for multiple articles via `config.yaml`.
- **Customizable Prompts:** All AI instructions are stored in `prompts.yaml` so you can tweak the agent personalities without touching the code!
- **Featured Image Integration:** Automatically fetches a high-quality free stock photo from Pexels OR generates a custom image via OpenAI DALL-E 3, and uploads it to the WordPress Media Library.
- **WordPress Integration:** Automatically assigns categories/tags and publishes the generated article directly to your WordPress site as a Draft.

## 📋 Prerequisites

Before you begin, ensure you have met the following requirements:
- Python 3.8+ installed on your machine.
- A WordPress website.
- A **Google Gemini API Key**. You can get one from [Google AI Studio](https://aistudio.google.com/).
- **(Optional) Image Generation APIs:**
  - A **Pexels API Key** for free stock photos. Get it at [Pexels API](https://www.pexels.com/api/).
  - An **OpenAI API Key** for DALL-E 3 AI image generation.
  - *Note: If you provide neither, the script safely generates text-only articles. If you provide both, the script will ask you which one to use when it runs!*
- A **WordPress Application Password**.
  - Go to your WordPress Admin Dashboard.
  - Navigate to **Users** -> **Profile**.
  - Scroll down to **Application Passwords**.
  - Enter a name (e.g., "Modawen Agent") and click **Add New Application Password**. Save this password.

## 🚀 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Mohamed-Elgaraihy/Modawen_Agent-For-Wordpress.git
   cd Modawen_Agent-For-Wordpress
   ```

2. **Create a virtual environment (Recommended):**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configuration:**
   Rename the `.env_example` file to `.env` and fill in your credentials:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   WP_URL=https://your-wordpress-site.com
   WP_USERNAME=your_wp_username
   WP_APP_PASSWORD=your_wp_application_password_here
   PEXELS_API_KEY=your_pexels_api_key_here
   OPENAI_IMAGE_API_KEY=your_openai_api_key_here
   ```

5. **Advanced Settings (Optional):**
   - Edit `config.yaml` to change the search query, target language, and number of articles to generate.
   - Edit `prompts.yaml` to tweak the AI's behavior and writing style.

## 💻 Usage

Run the main script to start the agent pipeline:

```bash
python main.py
```

The script will output its progress in the terminal. Once finished, check your WordPress dashboard under **Posts** -> **All Posts** to find your new draft!

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!
Feel free to check [issues page](https://github.com/Mohamed-Elgaraihy/Modawen_Agent-For-Wordpress/issues).

## 👨‍💻 Author

**Mohamed Elgaraihy**
* X / Twitter: [@EngMoElgaraihy](https://x.com/EngMoElgaraihy)
* GitHub: [@Mohamed-Elgaraihy](https://github.com/Mohamed-Elgaraihy)

## 📝 License

This project is open-source and available under the [MIT License](LICENSE).
