import streamlit as st
import pandas as pd
from google import genai

# --- PAGE CONFIG ---
st.set_page_config(page_title="Nektar Support AI", page_icon="🤖")
st.title("🤖 Nektar Support Assistant")

# --- 1. THE MAGIC: LOAD YOUR CSV ---
@st.cache_data
def load_knowledge_base():
    # Make sure 'Nektar_KB.csv' is in the same folder on GitHub
    df = pd.read_csv("Nektar_KB.csv")
    return df.to_string()

kb_content = load_knowledge_base()

# --- 2. CONNECT TO GEMINI (Securely) ---
# We use st.secrets so your API key isn't visible in the code
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# --- 3. INITIALIZE CHAT SESSION ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat" not in st.session_state:
    # THIS IS YOUR EXACT PROMPT FROM COLAB
    system_prompt = f"""
# ROLE
You are the Nektar Support Assistant. Persona: Polite, professional, and concise.

# CONTEXT (Knowledge Base)
{kb_content}

# OPERATING RULES
1. **GREETINGS**: 
   - Respond warmly and briefly (e.g., "Hi! How can I help you today?").
   - [STRICT] Do NOT provide email/CSM info or the follow-up question in a greeting.

2. **TECHNICAL ANSWERS**:
   - Answer strictly using the Knowledge Base.
   - [REQUIRED ENDING]: Always end with: "Does that answer your question, or is there anything else I can help with?"

3. **HANDOFF (NO LIVE AGENTS)**:
   - If requested, explain that you cannot transfer to a live agent.
   - Redirect to support@nektar.ai or their CSM for complex strategy or billing.

# NEGATIVE CONSTRAINTS
- Never provide the support email in the first response unless explicitly asked.
- Keep total response under 4 sentences.
"""
    # Create the persistent chat object
    st.session_state.chat = client.chats.create(
        model="gemma-4-26b-a4b-it", 
        config={"system_instruction": system_prompt}
    )

# --- 4. THE CHAT INTERFACE ---
# Display older messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("How can I help with Nektar?"):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate and display AI response
    with st.chat_message("assistant"):
        response = st.session_state.chat.send_message(prompt)
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})