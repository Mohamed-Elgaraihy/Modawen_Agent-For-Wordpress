import streamlit as st
import yaml
import os
import sys
import threading
from dotenv import set_key, dotenv_values
from config import CONFIG_FILE, logger

# Constants
ENV_FILE = ".env"

# Setup page configuration
st.set_page_config(
    page_title="Modawen Agent v2.1",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header { font-size: 2.5rem; font-weight: bold; color: #1E3A8A; margin-bottom: 0px; }
    .sub-header { font-size: 1.2rem; color: #6B7280; margin-bottom: 2rem; }
    .stButton>button { width: 100%; background-color: #2563EB; color: white; font-weight: bold; border-radius: 8px; padding: 0.75rem; }
    .stButton>button:hover { background-color: #1D4ED8; }
</style>
""", unsafe_allow_html=True)

# Helper Functions
def load_yaml_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        return {}

def save_yaml_config(data):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False)
        return True
    except Exception as e:
        return False

# Load current configs
config_data = load_yaml_config()
if "agent_settings" not in config_data: config_data["agent_settings"] = {}
if "schedule_settings" not in config_data: config_data["schedule_settings"] = {}

agent_settings = config_data["agent_settings"]
schedule_settings = config_data["schedule_settings"]

# Read current .env safely
env_dict = dotenv_values(ENV_FILE) if os.path.exists(ENV_FILE) else {}

# Header
st.markdown('<div class="main-header">🤖 Modawen Agent Control Panel</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Automate your WordPress content generation with AI.</div>', unsafe_allow_html=True)

# Define Tabs in the new logical order
tab1, tab2, tab3 = st.tabs(["🔐 Step 1: System Configuration", "⚙️ Step 2: Content Strategy", "🚀 Step 3: Execution Engine"])

# ==========================================
# TAB 1: System Configuration
# ==========================================
with tab1:
    st.subheader("Step 1: System Credentials")
    st.markdown("Securely manage your WordPress connection and API keys. These are saved to your local `.env` file.")
    
    with st.form("env_form"):
        st.markdown("#### WordPress Settings")
        wp_url = st.text_input("WordPress URL (e.g. https://yoursite.com)", value=env_dict.get("WP_URL", ""))
        wp_user = st.text_input("WordPress Username", value=env_dict.get("WP_USERNAME", ""))
        wp_pass = st.text_input("WordPress Application Password", value=env_dict.get("WP_APP_PASSWORD", ""), type="password")
        
        st.markdown("#### API Keys")
        gemini_key = st.text_input("Google Gemini API Key", value=env_dict.get("GEMINI_API_KEY", ""), type="password")
        openai_key = st.text_input("OpenAI API Key (GPT-4 / DALL-E)", value=env_dict.get("OPENAI_API_KEY", ""), type="password")
        anthropic_key = st.text_input("Anthropic API Key (Claude)", value=env_dict.get("ANTHROPIC_API_KEY", ""), type="password")
        pexels_key = st.text_input("Pexels API Key", value=env_dict.get("PEXELS_API_KEY", ""), type="password")
        
        if st.form_submit_button("Save System Configuration"):
            # Ensure .env exists
            if not os.path.exists(ENV_FILE):
                open(ENV_FILE, 'w').close()
                
            set_key(ENV_FILE, "WP_URL", wp_url)
            set_key(ENV_FILE, "WP_USERNAME", wp_user)
            set_key(ENV_FILE, "WP_APP_PASSWORD", wp_pass)
            set_key(ENV_FILE, "GEMINI_API_KEY", gemini_key)
            set_key(ENV_FILE, "OPENAI_API_KEY", openai_key)
            set_key(ENV_FILE, "ANTHROPIC_API_KEY", anthropic_key)
            set_key(ENV_FILE, "PEXELS_API_KEY", pexels_key)
            
            st.success("Credentials securely saved to .env!")
            st.rerun()

# ==========================================
# TAB 2: Content Strategy
# ==========================================
with tab2:
    st.subheader("Step 2: Content & AI Strategy")
    with st.form("strategy_form"):
        search_query = st.text_input("Search Topic", value=agent_settings.get("search_query", "latest AI trends"))
        
        langs = ["Arabic", "English", "French", "Spanish"]
        curr_lang = agent_settings.get("target_language", "Arabic")
        curr_lang_idx = langs.index(curr_lang) if curr_lang in langs else 0
        target_language = st.selectbox("Target Language", langs, index=curr_lang_idx)
        
        num_articles = st.number_input("Number of Articles per run", min_value=1, max_value=20, value=agent_settings.get("number_of_articles", 1))
        
        st.markdown("---")
        st.write("**AI Model Configuration**")
        providers = ["gemini", "openai", "anthropic"]
        curr_prov = agent_settings.get("llm_provider", "gemini").lower()
        curr_prov_idx = providers.index(curr_prov) if curr_prov in providers else 0
        llm_provider = st.selectbox("Text Generator (Articles)", providers, index=curr_prov_idx)
        
        img_providers = ["openai", "pexels"]
        curr_img = agent_settings.get("image_provider", "openai").lower()
        curr_img_idx = img_providers.index(curr_img) if curr_img in img_providers else 0
        image_provider = st.selectbox("Image Generator (Featured Image)", img_providers, index=curr_img_idx)
        
        st.markdown("---")
        st.write("**VPS Autopilot (Daily Scheduler)**")
        schedule_enabled = st.checkbox("Enable Daily Scheduler", value=schedule_settings.get("enabled", False))
        
        # Parse existing time
        import datetime
        default_time = None
        try:
            if schedule_settings.get("time"):
                h, m = map(int, schedule_settings.get("time").split(":"))
                default_time = datetime.time(h, m)
        except:
            pass
        schedule_time = st.time_input("Run Time", value=default_time)
        
        if st.form_submit_button("Save Strategy"):
            config_data["agent_settings"]["search_query"] = search_query
            config_data["agent_settings"]["target_language"] = target_language
            config_data["agent_settings"]["number_of_articles"] = num_articles
            config_data["agent_settings"]["llm_provider"] = llm_provider
            config_data["agent_settings"]["image_provider"] = image_provider
            
            config_data["schedule_settings"]["enabled"] = schedule_enabled
            if schedule_time:
                config_data["schedule_settings"]["time"] = schedule_time.strftime("%H:%M")
                
            if save_yaml_config(config_data):
                st.success("Strategy saved successfully!")
                st.rerun()

    # Dynamic Validation Warning
    curr_llm = agent_settings.get("llm_provider", "gemini").lower()
    missing_key = False
    if curr_llm == "gemini" and not env_dict.get("GEMINI_API_KEY"): missing_key = True
    if curr_llm == "openai" and not env_dict.get("OPENAI_API_KEY"): missing_key = True
    if curr_llm == "anthropic" and not env_dict.get("ANTHROPIC_API_KEY"): missing_key = True
    
    if missing_key:
        st.warning(f"⚠️ You selected **{curr_llm.upper()}**, but the API key is missing! Please configure it in the **System Configuration** tab.")

# ==========================================
# TAB 3: Execution Engine
# ==========================================
with tab3:
    st.subheader("Step 3: Run Modawen Agent")
    st.markdown("Trigger the 5-Agent pipeline to research, write, and publish to your WordPress site.")
    
    colA, colB = st.columns([1, 2])
    with colA:
        st.info(f"**Target Site:** {env_dict.get('WP_URL', 'Not Configured')}")
        st.info(f"**AI Model:** {agent_settings.get('llm_provider', 'gemini').upper()}")
        run_btn = st.button("Trigger Agents Now")
        
    with colB:
        st.write("Live Output Terminal:")
        log_container = st.empty()
        
        if run_btn:
            log_container.info("Initializing Agent Pipeline... Please wait.")
            class StreamlitRedirect:
                def __init__(self, widget):
                    self.widget = widget
                    self.text = ""
                    self.encoding = "utf-8"
                def write(self, s):
                    if s.strip():
                        self.text += s + "\\n"
                        lines = self.text.split('\\n')
                        if len(lines) > 100: self.text = '\\n'.join(lines[-100:])
                        self.widget.code(self.text, language="bash")
                def flush(self): pass
                    
            output_widget = st.empty()
            st_redirect = StreamlitRedirect(output_widget)
            
            try:
                import main
                old_stdout = sys.stdout
                sys.stdout = st_redirect
                
                # Force reload of configs
                import importlib
                import config
                import agents
                importlib.reload(config)
                importlib.reload(agents)
                importlib.reload(main)
                
                main.run_agent_pipeline()
                
                sys.stdout = old_stdout
                st.success("🎉 Pipeline execution completed successfully! Check your WordPress drafts.")
            except Exception as e:
                sys.stdout = old_stdout
                st.error(f"Execution failed: {e}")

st.markdown("---")
st.markdown("Modawen Agent v2.1.3 - Developed by Mohamed Elgaraihy")
