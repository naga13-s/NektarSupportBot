import streamlit as st
from google import genai
from PIL import Image

# --- 1. PAGE CONFIG ---
st.set_page_config(
    page_title="Nektar Support Assistant", 
    page_icon="🤖", 
    layout="centered"
)

# --- 2. THEME CUSTOMIZATION (Fixed parameter name) ---
css_style = """
    <style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stChatMessage"]:nth-child(odd) div.stMarkdown {
        background-color: #f1f3f5;
        border-radius: 15px;
        padding: 15px;
    }
    [data-testid="stChatMessage"]:nth-child(even) div.stMarkdown {
        background-color: #003049;
        color: #FFFFFF !important;
        border-radius: 15px;
        padding: 15px;
    }
    [data-testid="stChatMessage"]:nth-child(even) p {
        color: #FFFFFF !important;
    }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
"""
# CHANGED: unsafe_allow_html=True
st.markdown(css_style, unsafe_allow_html=True)

# --- 3. LOGO & HEADER ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try:
        # Matches your uploaded filename: Nektar-Logo.svg
        img = Image.open('Nektar-Logo.svg')
        st.image(img, use_container_width=True)
    except Exception:
        st.header("Nektar Support")

st.caption("Empowering your Salesforce workflow with AI.")

# --- 4. DATA LOADING ---
@st.cache_data
def load_kb():
    kb_file = "Knowledgebase dc271e4f7851429f9973cdf41d1e203a.md"
    try:
        with open(kb_file, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return "Knowledge base currently unavailable."

kb_content = load_kb()

# --- 5. CLIENT & CHAT INITIALIZATION ---
if "client" not in st.session_state:
    if "GEMINI_API_KEY" in st.secrets:
        st.session_state.client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    else:
        st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat" not in st.session_state:
    system_prompt = f"""
    # ROLE: Nektar Support Assistant. 
    # CONTEXT: {kb_content}
    # INSTRUCTIONS: Be professional and concise. 
    # End technical answers with: "Does that answer your question, or is there anything else I can help with?"
    """
    st.session_state.chat = st.session_state.client.chats.create(
        model="gemma-4-26b-a4b-it", 
        config={"system_instruction": system_prompt}
    )

# --- 6. THE CHAT INTERFACE ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("How can I help today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            response = st.session_state.chat.send_message(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception:
            st.markdown("I'm having a slight connection issue. Please try again!")
