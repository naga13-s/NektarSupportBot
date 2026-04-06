import streamlit as st
from google import genai
import base64
import re

# ─────────────────────────────────────────────
# 1. PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Nektar Support Assistant",
    page_icon="🤖",
    layout="centered",
)

# ─────────────────────────────────────────────
# 2. LOGO HELPER
#    The logo file is an SVG that wraps a base64 PNG.
#    We extract the PNG and render it directly so it
#    looks crisp on every background.
# ─────────────────────────────────────────────
@st.cache_data
def get_logo_base64(path: str = "nektar_logo.png") -> str | None:
    """
    Return a data-URI for the logo.
    Handles three cases:
      - Real PNG / JPEG  → encode directly
      - SVG with embedded base64 image → extract inner PNG
      - Plain SVG        → encode as image/svg+xml
    """
    try:
        raw = open(path, "rb").read()
    except FileNotFoundError:
        return None

    # Try to detect SVG (starts with < after optional BOM/whitespace)
    text = raw.decode("utf-8", errors="ignore").lstrip()
    if text.lstrip().startswith("<svg") or text.lstrip().startswith("<?xml"):
        # Look for an embedded base64 PNG inside the SVG
        match = re.search(
            r'xlink:href=["\']data:(image/[^;]+);base64,([^"\']+)["\']', text
        )
        if match:
            mime, b64 = match.group(1), match.group(2)
            return f"data:{mime};base64,{b64.strip()}"
        # Fall back: serve the whole SVG as a data-URI
        encoded = base64.b64encode(raw).decode()
        return f"data:image/svg+xml;base64,{encoded}"

    # Binary image (PNG, JPEG …)
    encoded = base64.b64encode(raw).decode()
    # Sniff magic bytes
    mime = "image/png" if raw[:4] == b"\x89PNG" else "image/jpeg"
    return f"data:{mime};base64,{encoded}"


LOGO_URI = get_logo_base64("nektar_logo.png")

# ─────────────────────────────────────────────
# 3. CUSTOM CSS  —  DARK THEME
# ─────────────────────────────────────────────
BG_PAGE     = "#0A0F1E"   # deep navy-black page background
BG_SURFACE  = "#111827"   # slightly lighter surface (sidebar / cards)
USER_BUBBLE = "#00A8E8"   # bright accent blue for user messages
BOT_BUBBLE  = "#1E293B"   # dark slate for assistant bubble
TEXT_MAIN   = "#E2E8F0"   # off-white — primary text
TEXT_MUTED  = "#64748B"   # muted grey for subtitles
ACCENT      = "#00A8E8"   # vibrant blue accent
INPUT_BG    = "#1E293B"   # dark input field background

st.markdown(
    f"""
    <style>
    /* ── Google Font ── */
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&display=swap');

    /* ── Global dark background ── */
    html, body, [class*="css"], .stApp, .main, .block-container {{
        font-family: 'DM Sans', sans-serif !important;
        background-color: {BG_PAGE} !important;
        color: {TEXT_MAIN} !important;
    }}

    /* Catch any rogue white panels */
    section[data-testid="stSidebar"],
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewBlockContainer"],
    [data-testid="stVerticalBlock"],
    [data-testid="stMain"] {{
        background-color: {BG_PAGE} !important;
    }}

    /* ── Hide Streamlit chrome ── */
    #MainMenu, footer, header {{ visibility: hidden; }}

    /* ── Header bar ── */
    .nk-header {{
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 18px 0 10px 0;
        border-bottom: 2px solid {ACCENT};
        margin-bottom: 12px;
    }}
    .nk-header img {{
        height: 36px;
        object-fit: contain;
        filter: brightness(1.1);
    }}
    .nk-title {{
        font-size: 1.25rem;
        font-weight: 600;
        color: {TEXT_MAIN} !important;
        letter-spacing: -0.02em;
    }}
    .nk-subtitle {{
        font-size: 0.78rem;
        color: {TEXT_MUTED} !important;
        margin-top: 2px;
    }}

    /* ── Chat message container ── */
    [data-testid="stChatMessage"] {{
        background: transparent !important;
    }}

    /* ── User bubble → accent blue, right side ── */
    [data-testid="stChatMessage"][data-role="user"] {{
        flex-direction: row-reverse;
    }}
    [data-testid="stChatMessage"][data-role="user"] .stMarkdown p {{
        background: {USER_BUBBLE} !important;
        color: #FFFFFF !important;
        border-radius: 18px 18px 4px 18px;
        padding: 10px 16px;
        display: inline-block;
        max-width: 85%;
        font-size: 0.93rem;
        line-height: 1.55;
    }}

    /* ── Assistant bubble → dark slate, left side ── */
    [data-testid="stChatMessage"][data-role="assistant"] .stMarkdown p,
    [data-testid="stChatMessage"][data-role="assistant"] .stMarkdown li,
    [data-testid="stChatMessage"][data-role="assistant"] .stMarkdown h1,
    [data-testid="stChatMessage"][data-role="assistant"] .stMarkdown h2,
    [data-testid="stChatMessage"][data-role="assistant"] .stMarkdown h3,
    [data-testid="stChatMessage"][data-role="assistant"] .stMarkdown span,
    [data-testid="stChatMessage"][data-role="assistant"] .stMarkdown {{
        color: {TEXT_MAIN} !important;
    }}
    [data-testid="stChatMessage"][data-role="assistant"] .stMarkdown p {{
        background: {BOT_BUBBLE} !important;
        color: {TEXT_MAIN} !important;
        border-radius: 18px 18px 18px 4px;
        padding: 10px 16px;
        display: inline-block;
        max-width: 88%;
        font-size: 0.93rem;
        line-height: 1.55;
        border: 1px solid #2D3748;
    }}

    /* ── Chat input — dark styled ── */
    [data-testid="stChatInput"] {{
        background-color: {INPUT_BG} !important;
        border-radius: 24px !important;
        border: 1.5px solid #2D3748 !important;
    }}
    [data-testid="stChatInput"] textarea {{
        background-color: {INPUT_BG} !important;
        color: {TEXT_MAIN} !important;
        border-radius: 24px !important;
        border: none !important;
        padding: 10px 18px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.93rem !important;
    }}
    [data-testid="stChatInput"] textarea:focus {{
        outline: none !important;
        box-shadow: 0 0 0 3px rgba(0,168,232,0.2) !important;
    }}
    [data-testid="stChatInput"] textarea::placeholder {{
        color: {TEXT_MUTED} !important;
    }}

    /* ── Scrollbar ── */
    ::-webkit-scrollbar {{ width: 6px; }}
    ::-webkit-scrollbar-track {{ background: {BG_PAGE}; }}
    ::-webkit-scrollbar-thumb {{ background: #2D3748; border-radius: 8px; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# 4. HEADER
# ─────────────────────────────────────────────
logo_html = (
    f'<img src="{LOGO_URI}" alt="Nektar logo">'
    if LOGO_URI
    else '<span style="font-size:1.6rem">🤖</span>'
)

st.markdown(
    f"""
    <div class="nk-header">
        {logo_html}
        <div>
            <div class="nk-title">Support Assistant</div>
            <div class="nk-subtitle">Empowering your Salesforce workflow with AI</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# 5. KNOWLEDGE BASE
# ─────────────────────────────────────────────
@st.cache_data
def load_kb() -> str:
    kb_file = "Knowledgebase dc271e4f7851429f9973cdf41d1e203a.md"
    try:
        with open(kb_file, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Knowledge base currently unavailable."

kb_content = load_kb()


@st.cache_data
def load_faq() -> str:
    try:
        with open("faq.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

faq_content = load_faq()

# ─────────────────────────────────────────────
# 6. GEMINI CLIENT & SESSION INIT
# ─────────────────────────────────────────────
if "client" not in st.session_state:
    if "GEMINI_API_KEY" not in st.secrets:
        st.error("⚠️ GEMINI_API_KEY is missing from Streamlit secrets.", icon="🔑")
        st.stop()
    st.session_state.client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat" not in st.session_state:
    system_prompt = f"""
# ROLE
You are the Nektar Support Assistant. Think of yourself as a knowledgeable, friendly colleague helping a teammate with Nektar.

# FAQ (answer these instantly without searching the knowledge base)
   
   {faq_content}

# CONTEXT
{kb_content}

# CONVERSATIONAL GUIDELINES
1. **GREETINGS & PERMISSIONS**:
   - If someone says "hi" or asks "can I ask a question?", be warm and inviting.
   - Example: "Of course! I'm here to help. What's on your mind?"
   - [CRITICAL] Do NOT use a formal "Does that answer your question?" for simple greetings.

2. **TECHNICAL HELP**:
   - Give clear, helpful answers based on the Knowledge Base.
   - Keep it human: use phrases like "I see," "Great question," or "Based on our docs..."
   - [VARY THE CLOSING]: After a technical answer, check in naturally. Use phrases like:
     * "Does that clear things up for you?"
     * "Let me know if you need more detail on that!"
     * "Is there anything else I can double-check for you?"

3. **WHEN A HUMAN IS NEEDED**:
   - If they ask for a person or a "live agent," be honest:
     "I'm an Bot, so I can't jump into a live chat with you, but I don't want to leave you hanging!"
   - Direct them to **support@nektar.ai** or their **CSM** for things like billing, strategy, or complex setup.

4. # CONTACT INFORMATION
  - Support Email: support@nektar.ai
  - For billing, strategy, or complex setup → direct users to support@nektar.ai or their CSM.

# NEGATIVE CONSTRAINTS
- No "robot-speak." Avoid repeating the exact same closing sentence every single time.
- Never show the support email in the first greeting.
- Keep responses snappy (under 4 sentences).
""".strip()

    st.session_state.chat = st.session_state.client.chats.create(
        model="gemma-4-26b-a4b-it",
        config={"system_instruction": system_prompt},
    )

# ─────────────────────────────────────────────
# 7. RENDER CHAT HISTORY
# ─────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ─────────────────────────────────────────────
# 8. HANDLE NEW INPUT
# ─────────────────────────────────────────────
if prompt := st.chat_input("Ask me anything about Nektar…"):
    # Show user message immediately
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get assistant reply
    with st.chat_message("assistant"):
        with st.spinner(""):
            try:
                response = st.session_state.chat.send_message(prompt)
                reply = response.text
            except Exception as exc:
                reply = (
                    "I'm having a slight connection issue right now. "
                    "Please try again in a moment! 🙏"
                )
                st.error(f"Error details: {exc}", icon="⚠️")

        st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})
