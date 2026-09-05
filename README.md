# Modawen Agent for WordPress v4.1.1 🚀

[![Open Source Love](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://github.com/ellerbrock/open-source-badges/)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

**Modawen Agent for WordPress** is a completely autonomous, AI-powered multi-agent SaaS that researches live trends, writes deep-dive SEO-optimized articles, manages your WordPress site, and generates viral social media marketing entirely on autopilot.

Version 4.1.1 introduces **Dynamic Model Selection**, the brand new **Analytics Dashboard**, a **Social Media Marketing Agent**, and **DeepSeek Integration**!

## 🌟 How It Works
The system uses a massive **6-Agent Architecture**:
1. 🧠 **Topic Generator Agent:** Breaks down your broad niche into a randomized pool of highly specific search queries, ensuring zero duplicate content.
2. 🔍 **Technology Researcher Agent:** Scrapes live Google Search results to extract real-world facts and URLs (No AI hallucinations).
3. ✍️ **Content Writer Agent:** Transforms the research into a massive, heavily structured SEO-friendly article in your chosen language, embedding high-value outbound and internal HTML links.
4. 🎯 **Metadata & SEO Agent:** Generates an attractive title, creates SEO tags, and intelligently selects the best existing WordPress Category.
5. 🖼️ **Image Query Agent:** Uses OpenAI (GPT-4) or Pexels to generate the perfect stock photo matching the article.
6. 📱 **Social Media Agent (NEW!):** Reads your published article and instantly writes a viral, highly-engaging Twitter (X) thread to drive traffic to your site!

## ✨ New Features in v4.x
- **Dynamic 2026 AI Models:** Run the agents using the absolute latest flagship models of 2026 (e.g. `gpt-6-astra`, `gemini-3.0-pro`, `claude-4-opus`).
- **DeepSeek Integrated:** Full support for `deepseek-chat-v3`, the most powerful open-weight creative writer!
- **YouTube-to-Blog Override:** Paste a YouTube URL into the UI, and Modawen will ignore Google Search, automatically pull the video transcript (any language!), and turn the video into a massive SEO blog post!
- **Smart Internal Linking:** Modawen scans your existing WordPress database and automatically organically weaves internal links to your older posts into the new article!
- **Analytics Dashboard:** A beautiful UI tab that tracks your generation history and success rates using a local SQLite database.

## 📋 Prerequisites
- Python 3.8+
- A WordPress website.
- A **WordPress Application Password** (See Configuration below).
- At least ONE of the following API keys:
  - Google Gemini API Key
  - OpenAI API Key
  - Anthropic API Key
  - DeepSeek API Key

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

Simply run `streamlit run app.py` and open the **System Configuration** tab in your browser. You can type in your WordPress URL, Username, Application Passwords, and API Keys directly into the interface. It will automatically save them to your local system securely!

> ⚠️ **How to get `WP_APP_PASSWORD`**
> 1. Log in to your WordPress Admin Dashboard.
> 2. Go to **Users** -> **Profile**.
> 3. Scroll down to **Application Passwords**.
> 4. Enter a name (e.g., "Modawen") and click **Add New Application Password**.

## 💻 Usage

### 1. Web UI Mode (Recommended)
Launch the visual dashboard in your browser to configure dynamic models, view analytics, and trigger agents manually.
```bash
streamlit run app.py
```

### 2. Autopilot Mode (VPS / Server)
Leave this script running in the background on your server to automatically publish articles at your scheduled time. (Configure the time via the Web UI).
```bash
python scheduler.py
```

## 🤝 Contributions & Author

Created by **Mohamed Elgaraihy**
* X / Twitter: [@EngMoElgaraihy](https://x.com/EngMoElgaraihy)
* GitHub: [@Mohamed-Elgaraihy](https://github.com/Mohamed-Elgaraihy)

This project is open-source. We welcome pull requests, feature requests, and bug reports! If you use this tool, please consider starring the repository! ⭐
