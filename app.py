import streamlit as st
import yaml
import os
import sys
from config import CONFIG_FILE, WP_URL, logger
import threading
import contextlib
import io

# Setup page configuration
st.set_page_config(
    page_title="Modawen Agent v2.0",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A8A;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #6B7280;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #2563EB;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.75rem;
    }
    .stButton>button:hover {
        background-color: #1D4ED8;
    }
</style>
""", unsafe_allow_html=True)

def load_yaml_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        st.error(f"Failed to load config.yaml: {e}")
        return {}

def save_yaml_config(data):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False)
        return True
    except Exception as e:
        st.error(f"Failed to save config.yaml: {e}")
        return False

# Load current config
config_data = load_yaml_config()
agent_settings = config_data.get("agent_settings", {})
schedule_settings = config_data.get("schedule_settings", {})

# Header
st.markdown('<div class="main-header">🤖 Modawen Agent Control Panel</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Automate your WordPress content generation with AI.</div>', unsafe_allow_html=True)

# Layout
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("⚙️ Configuration")
    
    with st.form("config_form"):
        st.write("Agent Settings")
        search_query = st.text_input("Search Topic", value=agent_settings.get("search_query", "latest AI trends"))
        target_language = st.selectbox("Target Language", ["Arabic", "English", "French", "Spanish"], index=["Arabic", "English", "French", "Spanish"].index(agent_settings.get("target_language", "Arabic")) if agent_settings.get("target_language", "Arabic") in ["Arabic", "English", "French", "Spanish"] else 0)
        num_articles = st.number_input("Number of Articles (Loop)", min_value=1, max_value=20, value=agent_settings.get("number_of_articles", 1))
        
        provider_options = ["gemini", "openai", "anthropic"]
        llm_provider = st.selectbox("LLM Provider", provider_options, index=provider_options.index(agent_settings.get("llm_provider", "gemini").lower()) if agent_settings.get("llm_provider", "gemini").lower() in provider_options else 0)
        
        st.write("---")
        st.write("Autopilot Settings (VPS Scheduler)")
        schedule_enabled = st.checkbox("Enable Daily Scheduler", value=schedule_settings.get("enabled", False))
        schedule_time = st.time_input("Daily Run Time", value=None)
        # Parse existing time
        try:
            import datetime
            if schedule_settings.get("time"):
                h, m = map(int, schedule_settings.get("time").split(":"))
                schedule_time = datetime.time(h, m)
        except:
            pass

        submitted = st.form_submit_button("Save Settings")
        
        if submitted:
            config_data["agent_settings"]["search_query"] = search_query
            config_data["agent_settings"]["target_language"] = target_language
            config_data["agent_settings"]["number_of_articles"] = num_articles
            config_data["agent_settings"]["llm_provider"] = llm_provider
            
            config_data["schedule_settings"]["enabled"] = schedule_enabled
            if schedule_time:
                config_data["schedule_settings"]["time"] = schedule_time.strftime("%H:%M")
                
            if save_yaml_config(config_data):
                st.success("Settings saved successfully!")

    st.info(f"Target WordPress Site: **{WP_URL}**")

with col2:
    st.subheader("🚀 Execution Engine")
    
    run_btn = st.button("Trigger Agents Now")
    
    st.write("Live Output Terminal:")
    log_container = st.empty()
    
    if run_btn:
        log_container.info("Initializing Agent Pipeline... Please wait.")
        
        # We need to capture the stdout to display in the UI
        class StreamlitRedirect:
            def __init__(self, widget):
                self.widget = widget
                self.text = ""
                
            def write(self, s):
                if s.strip():
                    self.text += s + "\n"
                    # Keep only last 100 lines to prevent UI lag
                    lines = self.text.split('\n')
                    if len(lines) > 100:
                        self.text = '\n'.join(lines[-100:])
                    self.widget.code(self.text, language="bash")
                    
            def flush(self):
                pass
                
        output_widget = st.empty()
        st_redirect = StreamlitRedirect(output_widget)
        
        # Run in main thread but redirect stdout
        try:
            import main
            old_stdout = sys.stdout
            sys.stdout = st_redirect
            
            # Since main.py variables might be cached, we reload config inside run_agent_pipeline if needed,
            # but for this script, we can just call it and rely on its internal imports.
            import importlib
            importlib.reload(main) # Ensure fresh config load
            
            main.run_agent_pipeline()
            
            sys.stdout = old_stdout
            st.success("🎉 Pipeline execution completed successfully! Check your WordPress drafts.")
        except Exception as e:
            sys.stdout = old_stdout
            st.error(f"Execution failed: {e}")

st.markdown("---")
st.markdown("Modawen Agent v2.0 - Developed by Mohamed Elgaraihy")
