import streamlit as st
from google import genai
from PIL import Image

# --- 1. PAGE CONFIG (Clean & Professional) ---
st.set_page_config(
    page_title="Nektar Support Assistant", 
    page_icon="🤖", 
    layout="centered"
)

# --- 2. THEME CUSTOMIZATION (Nektar Branding) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    
    /* User Message Bubbles */
    [data-testid="stChatMessage"]:nth-child(odd) div.stMarkdown {
        background-color: #f1f3f5;
        border-radius: 15px;
        padding: 15px;
    }

    /* Assistant Message Bubbles (Nektar Navy) */
    [data-testid="stChatMessage"]:nth-child(even) div.stMarkdown {
        background-color: #003049;
        color: #FFFFFF !important;
        border-radius: 15px;
        padding: 15px;
    }
    
    /* Ensure text inside Assistant bubble is readable */
    [data-testid="stChatMessage"]:nth-child(even) p {
        color: #FFFFFF !important;
    }

    /* Hide Streamlit elements for a custom look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_index=True)

# --- 3. LOGO & HEADER ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try:
        # Ensure 'nektar_logo.png' is uploaded to your GitHub repo
        img = Image.open('nektar_logo.png')
        st.image(img, use_container_width=True)
    except:
        st.header("Nektar Support")

st.caption("Empowering your Salesforce workflow with AI.")

# --- 4. DATA LOADING ---
@st.cache_data
def load_kb():
    # Matches your exact filename from GitHub
    kb_file = "Knowledgebase dc271e4f7851429f9973cdf41d1e203a.md"
    try:
        with open(kb_file, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "Knowledge base currently unavailable."

kb_content = load_kb()

# --- 5. CLIENT & CHAT INITIALIZATION ---
if "client" not in st.session_state:
    if "GEMINI_API_KEY" in st.secrets:
        st.session_state.client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    else:
        st.error("API Key missing in Secrets.")
        st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat" not in st.session_state:
    system_prompt = f"""
    # ROLE: Nektar Support Assistant. Persona: Professional and concise.
    # CONTEXT: {kb_content}
    # INSTRUCTIONS: Be conversational. If asked for a live person, redirect to support@nektar.ai or their CSM. 
    # End technical answers with: "Does that answer your question, or is there anything else I can help with?"
    """
    st.session_state.chat = st.session_state.client.chats.create(
        model="gemma-4-26b-a4b-it", 
        config={"system_instruction": system_prompt}
    )

# --- 6. THE CHAT INTERFACE (The fix is here) ---
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
        except:
            st.markdown("I'm having a slight connection issue. Please try again in a moment!")
