# Modawen Agent for WordPress v2.0 🚀

[![Open Source Love](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://github.com/ellerbrock/open-source-badges/)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

**Modawen Agent for WordPress** is a completely autonomous, AI-powered multi-agent system that researches live trends, writes deep-dive SEO-optimized articles, generates custom featured images, and manages your WordPress site entirely on autopilot.

Version 2.0 introduces **Multi-LLM Support**, a gorgeous **Web Interface**, and a **VPS Autopilot Scheduler**.

## 🌟 How It Works
The system uses a **5-Agent Architecture**:
1. 🧠 **Topic Generator Agent:** Breaks down your broad niche into a randomized pool of highly specific search queries, ensuring zero duplicate content.
2. 🔍 **Technology Researcher Agent:** Scrapes live Google Search results to extract real-world facts (No AI hallucinations).
3. ✍️ **Content Writer Agent:** Transforms the research into a massive (1,200+ words), SEO-friendly article in your chosen language, embedding high-value outbound HTML links.
4. 🎯 **Metadata & SEO Agent:** Generates an attractive title, creates SEO tags, and intelligently selects the best existing WordPress Category.
5. 🖼️ **Image Query Agent:** Uses OpenAI (GPT-4) or Pexels to generate the perfect stock photo matching the article.

## ✨ Version 2.0 Features
- **Multi-LLM Engine:** Run the agents using Google Gemini, OpenAI (GPT-4o), or Anthropic (Claude 3.5).
- **Streamlit Web UI:** A complete visual dashboard. Edit configurations, toggle AI models, and trigger generation directly from your web browser.
- **VPS Autopilot Scheduler:** Deploy to a Virtual Private Server (VPS), set a time in the Web UI, and let the background worker publish articles daily while you sleep.

## 📋 Prerequisites
- Python 3.8+
- A WordPress website.
- A **WordPress Application Password** (See Configuration below).
- At least ONE of the following API keys:
  - Google Gemini API Key
  - OpenAI API Key
  - Anthropic API Key

## 🚀 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Mohamed-Elgaraihy/Modawen_Agent-For-Wordpress.git
   cd Modawen_Agent-For-Wordpress
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Configuration

Rename the `.env_example` file to `.env` and fill in your credentials:
```env
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
WP_URL=https://your-wordpress-site.com
WP_USERNAME=your_wp_username
WP_APP_PASSWORD=your_wp_application_password
OPENAI_IMAGE_API_KEY=your_openai_image_key
PEXELS_API_KEY=your_pexels_key
```

> ⚠️ **How to get `WP_APP_PASSWORD`**
> 1. Log in to your WordPress Admin Dashboard.
> 2. Go to **Users** -> **Profile**.
> 3. Scroll down to **Application Passwords**.
> 4. Enter a name (e.g., "Modawen") and click **Add New Application Password**.

## 💻 Usage

Modawen v2.0 offers three powerful ways to run your AI factory:

### 1. Web UI Mode (Recommended)
Launch the visual dashboard in your browser to configure settings and trigger agents manually.
```bash
streamlit run app.py
```

### 2. Autopilot Mode (VPS / Server)
Leave this script running in the background on your server to automatically publish articles at your scheduled time. (Configure the time via the Web UI).
```bash
python scheduler.py
```

### 3. CLI Mode (Developers)
Run the pipeline directly from your terminal.
```bash
python main.py
```

## 🤝 Contributions & Author

Created by **Mohamed Elgaraihy**
* X / Twitter: [@EngMoElgaraihy](https://x.com/EngMoElgaraihy)
* GitHub: [@Mohamed-Elgaraihy](https://github.com/Mohamed-Elgaraihy)

This project is open-source. We welcome pull requests, feature requests, and bug reports! If you use this tool, please consider starring the repository! ⭐
