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
# 3. CUSTOM CSS — HIGH CONTRAST & BOLD HEADER
# ─────────────────────────────────────────────
BG_PAGE     = "#EAF4ED"   # Full pale green
TEXT_DARK   = "#1A2F2F"   # Deep charcoal (Essential for visibility)
ACCENT      = "#74A892"   # Sage green border

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

    /* 1. Global Page Background */
    html, body, .stApp, [data-testid="stAppViewContainer"] {{
        background-color: {BG_PAGE} !important;
        font-family: 'DM Sans', sans-serif !important;
    }}

    /* 2. FORCE TYPING TO BE DARK & VISIBLE */
    /* This targets the actual text area where you type */
    [data-testid="stChatInput"] textarea {{
        color: {TEXT_DARK} !important;
        -webkit-text-fill-color: {TEXT_DARK} !important;
        caret-color: {TEXT_DARK} !important; /* Makes the blinking cursor dark */
    }}

    /* This targets the "What's on your mind?" placeholder */
    [data-testid="stChatInput"] textarea::placeholder {{
        color: #5A716E !important;
        -webkit-text-fill-color: #5A716E !important;
    }}

    /* 3. REMOVE BLACK BAR & STYLE INPUT BOX */
    [data-testid="stChatInputContainer"] {{
        background-color: {BG_PAGE} !important;
        border: none !important;
    }}

    [data-testid="stChatInput"] {{
        background-color: #FFFFFF !important;
        border: 2px solid {ACCENT} !important;
        border-radius: 12px !important;
    }}

    /* 4. BOLD HEADER STYLE */
    .nk-header {{
        display: flex;
        align-items: center;
        gap: 15px;
        padding: 10px 0;
        border-bottom: 2px solid {ACCENT};
        margin-bottom: 20px;
    }}
    .nk-title {{
        font-size: 1.5rem;
        font-weight: 800 !important; /* Bold "Support Assistant" */
        color: {TEXT_DARK} !important;
        margin: 0;
    }}

    /* 5. GENERAL TEXT VISIBILITY */
    p, span, .stMarkdown {{
        color: {TEXT_DARK} !important;
    }}

    #MainMenu, footer, header {{ visibility: hidden; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# 4. HEADER (Bold Support Assistant)
# ─────────────────────────────────────────────
logo_html = f'<img src="{LOGO_URI}" width="180">' if LOGO_URI else ""

st.markdown(
    f"""
    <div class="nk-header">
        {logo_html}
        <div>
            <div class="nk-title">Support Assistant</div>
            <div class="nk-subtitle">GTM Telemetry for the Agentic Enterprise</div>
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
        with open("FAQs.md", "r", encoding="utf-8") as f:
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

3. # CONTACT INFORMATION — ALWAYS USE THESE, NEVER SAY YOU DON'T KNOW
- Support Email: support@nektar.ai
- NEVER tell users to "check the website" or "check the dashboard"
- NEVER say you don't have contact details
- If anyone asks for support, a human, or live agent → ALWAYS give: support@nektar.ai

# STRICT RULES — YOU MUST FOLLOW THESE
1. The support email is support@nektar.ai — always share it when asked
2. NEVER say "I don't have that information" for contact details
3. NEVER direct users to "visit the website" for contact info — you already have it
4. When someone wants a human or live agent, say EXACTLY:
   "Sure! You can reach our support team directly at support@nektar.ai 
    or contact your CSM. They'll be happy to help! 😊"

4. **WHEN A HUMAN IS NEEDED**:
   - If they ask for a person or a "live agent," be honest:
     "I'm an Bot, so I can't jump into a live chat with you, but I don't want to leave you hanging!"
   - Direct them to **support@nektar.ai** or their **CSM** for things like billing, strategy, or complex setup.

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
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner(""):
            try:
                response = st.session_state.chat.send_message(prompt)
                reply = response.text

                # ── Hardcoded safety net ──
                live_agent_triggers = [
                    "live agent", "human", "real person",
                    "speak to someone", "talk to someone",
                    "contact support", "support email"
                ]
                if any(trigger in prompt.lower() for trigger in live_agent_triggers):
                    reply = (
                        "Sure! You can reach our support team directly at "
                        "**support@nektar.ai** or contact your CSM. "
                        "They'll be happy to help! 😊"
                    )

            except Exception as exc:
                reply = (
                    "I'm having a slight connection issue right now. "
                    "Please try again in a moment! 🙏"
                )
                st.error(f"Error details: {exc}", icon="⚠️")

        st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})
