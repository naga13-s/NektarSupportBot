import streamlit as st
from google import genai
from PIL import Image

# --- PAGE CONFIG (Clean & Nice UI) ---
st.set_page_config(
    page_title="Nektar Support Assistant", 
    page_icon="🤖", 
    layout="centered"
)

# --- THEME CUSTOMIZATION: Nektar Colors ---
# Yellow: #FFD200, Navy: #003049, White: #FFFFFF
st.markdown("""
    <style>
    /* 1. Main Background */
    .stApp {
        background-color: #FFFFFF;
    }

    /* 2. Chat Bubbles: User */
    [data-testid="stChatMessage"] div.stMarkdown {
        background-color: #f1f3f5;
        border-radius: 12px;
        padding: 10px;
    }

    /* 3. Chat Bubbles: Assistant (Nektar Blue) */
    [data-testid="stChatMessage"]:nth-child(even) div.stMarkdown {
        background-color: #003049;
        color: #FFFFFF !important;
        border-radius: 12px;
        padding: 10px;
    }
    
    /* Ensure markdown text is white in Assistant bubble */
    [data-testid="stChatMessage"]:nth-child(even) p {
        color: #FFFFFF !important;
    }

    /* 4. Hide Default Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stChatFloatingInputContainer {padding-bottom: 20px;}

    /* 5. Clean up Header Spacing */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 0rem;
    }
    </style>
    """, unsafe_allow_index=True)

# --- 1. THE LOGO & HEADER ---
# Centering the logo using columns
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    # Ensure 'nektar_logo.png' is in the same folder on GitHub
    try:
        image = Image.open('nektar_logo.png')
        st.image(image, use_column_width=True)
    except:
        st.write("Nektar Support") # Fallback if logo is missing
st.title("🤖 Nektar Support AI")
st.caption("Ask me about Nektar features, setup, or strategy.")

# --- 2. SILENT DATA LOAD ---
@st.cache_data
def load_kb():
    # Silent load - no error logs shown to the user
    kb_filename = "Knowledgebase dc271e4f7851429f9973cdf41d1e203a.md"
    try:
        with open(kb_filename, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "Knowledge base unavailable."

kb_content = load_kb()

# --- 3. SILENT CLIENT INIT ---
if "client" not in st.session_state:
    if "GEMINI_API_KEY" in st.secrets:
        st.session_state.client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    else:
        st.stop() # Stops the app quietly if key is missing

# --- 4. CHAT HISTORY & SYSTEM PROMPT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat" not in st.session_state:
    system_prompt = f"""
    # ROLE: Nektar Support Assistant. Persona: Polite, professional, and concise.
    # CONTEXT: {kb_content}
    # RULES: Follow the conversational guidelines we discussed...
    """
    st.session_state.chat = st.session_state.client.chats.create(
        model="gemma-4-26b-a4b-it", 
        config={"system_instruction": system_prompt}
    )

# --- 5. THE CHAT INTERFACE (No Logs) ---
for message in st
