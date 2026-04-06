import streamlit as st
from google import genai

# --- PAGE CONFIG ---
st.set_page_config(page_title="Nektar Support AI", page_icon="🤖")
st.title("🤖 Nektar Support Assistant")

# --- 1. LOAD THE MARKDOWN KNOWLEDGE BASE ---
@st.cache_data
def load_kb():
    # Make sure this filename matches your uploaded file exactly!
    kb_filename = "Knowledgebase dc271e4f7851429f9973cdf41d1e203a.md"
    try:
        with open(kb_filename, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        st.error(f"Could not find {kb_filename}. Please check the filename in GitHub.")
        return ""

kb_content = load_kb()

# --- 2. CONNECT TO GEMINI ---
# Ensure you add 'GEMINI_API_KEY' in Streamlit Cloud Settings > Secrets
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# --- 3. INITIALIZE SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat" not in st.session_state:
    system_prompt = f"""
# ROLE
You are the Nektar Support Assistant. Persona: Polite, professional, and concise.

# CONTEXT (Knowledge Base)
{kb_content}

# OPERATING RULES
1. **GREETINGS & PERMISSIONS**:
   - If someone says "hi" or asks "can I ask a question?", be warm and inviting. 
   - [STRICT] Do NOT use technical follow-up questions for simple greetings.

2. **TECHNICAL HELP**:
   - Use the Knowledge Base to provide clear, helpful answers.
   - [VARY THE CLOSING]: After a technical answer, end with something like:
     * "Does that clear things up for you?"
     * "Is there anything else I can double-check for you?"

3. **HANDOFF (NO LIVE AGENTS)**:
   - If they ask for a person, explain that you are an AI assistant.
   - Redirect them to email support@nektar.ai or contact their CSM for complex issues.

# NEGATIVE CONSTRAINTS
- Never provide the support email in the first greeting.
- Keep responses under 4 sentences.
"""
    st.session_state.chat = client.chats.create(
        model="gemma-4-26b-a4b-it", 
        config={"system_instruction": system_prompt}
    )

# --- 4. THE CHAT INTERFACE ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("How can I help with Nektar today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = st.session_state.chat.send_message(prompt)
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
