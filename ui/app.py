import json
import os
from datetime import datetime
from pathlib import Path

import requests
import streamlit as st

# ==================================================
# 1. CONFIGURATION
# ==================================================

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
FEEDBACK_FILE = Path(__file__).resolve().parent / "feedback.json"

st.set_page_config(
    page_title="AyushmanSathi | Healthcare Assistant",
    page_icon=":hospital:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==================================================
# 2. CUSTOM CSS
# ==================================================

st.markdown("""
<style>
/* ---- Global ---- */
.block-container {
    padding-top: 3rem !important;
    padding-bottom: 2rem !important;
    max-width: 1080px;
}
.stApp {
    background: #F4F8F7;
    font-family: "Segoe UI", Arial, sans-serif;
    color: #1E3A3F;
}

/* ---- Sidebar ---- */
[data-testid="stSidebar"] {
    background: #FFFFFF;
    border-right: 1px solid #E0EDEA;
}
[data-testid="stSidebar"] .stMarkdown h1 {
    font-size: 20px;
    font-weight: 700;
    color: #1A7A5E;
    margin-bottom: 2px;
}
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stCaptionContainer {
    color: #6B8C88;
    font-size: 13px;
}
[data-testid="stSidebar"] .stMarkdown h3 {
    font-size: 13px;
    font-weight: 700;
    color: #2C5F5A;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 0;
    margin-bottom: 6px;
}
/* Radio nav buttons */
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    font-size: 14px;
    color: #2C5050;
    padding: 6px 10px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: #EEF7F3;
}
/* Sidebar footer badge */
.sidebar-badge {
    background: #EBF5F0;
    border: 1px solid #B6DDD0;
    border-radius: 12px;
    padding: 12px 14px;
    display: flex;
    align-items: flex-start;
    gap: 10px;
    margin-top: 4px;
}
.sidebar-badge-icon {
    font-size: 22px;
    line-height: 1;
    margin-top: 2px;
}
.sidebar-badge-text {
    font-size: 12.5px;
    color: #2A6050;
    line-height: 1.5;
}

/* ---- Hero card ---- */
.hero-card {
    background: linear-gradient(135deg, #E8F5EE 0%, #F0FAF6 100%);
    border: 1px solid #C8E8DC;
    border-left: 5px solid #1A9E6E;
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 28px;
}
.hero-label {
    font-size: 14px;
    color: #1A9E6E;
    font-weight: 600;
    margin-bottom: 4px;
}
.hero-title {
    font-size: 34px;
    font-weight: 800;
    color: #0F2E35;
    line-height: 1.15;
    margin-bottom: 6px;
    letter-spacing: -0.5px;
}
.hero-subtitle {
    font-size: 16px;
    color: #2A5D58;
    font-weight: 500;
    margin-bottom: 12px;
}
.hero-body {
    font-size: 14px;
    color: #4A7070;
    line-height: 1.65;
    max-width: 620px;
}

/* ---- Section heading ---- */
.section-heading {
    font-size: 20px;
    font-weight: 700;
    color: #0F2E35;
    border-left: 4px solid #1A9E6E;
    padding-left: 12px;
    margin: 28px 0 16px 0;
    line-height: 1.3;
}

/* ---- Service cards ---- */
.svc-card {
    background: #FFFFFF;
    border: 1px solid #DCF0E8;
    border-radius: 14px;
    padding: 22px 24px;
    min-height: 110px;
    box-shadow: 0 2px 8px rgba(26,158,110,0.05);
    margin-bottom: 14px;
    transition: box-shadow 0.2s, border-color 0.2s;
}
.svc-card:hover {
    border-color: #8DCFB5;
    box-shadow: 0 6px 18px rgba(26,158,110,0.10);
}
.svc-card h4 {
    font-size: 15px;
    font-weight: 700;
    color: #0F2E35;
    margin: 0 0 8px 0;
}
.svc-card p {
    font-size: 13px;
    color: #5A7D78;
    margin: 0;
    line-height: 1.55;
}

/* ---- Popular question buttons ---- */
div.stButton > button {
    background: #FFFFFF;
    border: 1px solid #D6EDE5;
    border-radius: 10px;
    color: #1E4040;
    font-size: 13.5px;
    font-weight: 500;
    text-align: left;
    padding: 10px 16px;
    width: 100%;
    min-height: 44px;
    box-shadow: 0 1px 4px rgba(26,158,110,0.06);
    transition: background 0.15s, border-color 0.15s, box-shadow 0.15s;
}
div.stButton > button:hover {
    background: #EDF8F3;
    border-color: #8DCFB5;
    box-shadow: 0 3px 10px rgba(26,158,110,0.12);
    color: #0F3030;
}

/* ---- Chat messages ---- */
[data-testid="stChatMessage"] {
    background: #FFFFFF;
    border: 1px solid #E2EDEA;
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 8px;
}
[data-testid="stChatInput"] textarea {
    border-radius: 10px;
}

/* ---- Page heading / sub-heading ---- */
.page-heading {
    font-size: 26px;
    font-weight: 700;
    color: #0F2E35;
    margin-top: 2rem;
    margin-bottom: 4px;
    position: relative;
    z-index: 1;
}
.page-sub {
    font-size: 14px;
    color: #6A8C88;
    margin-bottom: 20px;
    position: relative;
    z-index: 1;
}

/* ---- About card ---- */
.about-card {
    background: linear-gradient(135deg, #E8F5EE 0%, #F0FAF6 100%);
    border: 1px solid #C8E8DC;
    border-left: 5px solid #1A9E6E;
    border-radius: 16px;
    padding: 24px 28px;
    margin-bottom: 20px;
}
.about-card h2 {
    font-size: 20px;
    font-weight: 700;
    color: #0F2E35;
    margin: 0 0 10px 0;
}
.about-card p {
    font-size: 14px;
    color: #4A7070;
    line-height: 1.65;
    margin: 0;
}

footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ==================================================
# 3. SESSION STATE
# ==================================================

defaults = {
    "messages": [],
    "page": "Home",
    "mode": "RAG Question Answering",
    "thread_id": "streamlit-session-1",
    "pending_question": "",
    "feedback_given": [],
    "pending_approval": None,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ==================================================
# 4. FEEDBACK STORAGE
# ==================================================

def save_feedback(question, answer, feedback):
    FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)
    data = []
    if FEEDBACK_FILE.exists():
        try:
            data = json.loads(FEEDBACK_FILE.read_text(encoding="utf-8"))
            if not isinstance(data, list):
                data = []
        except (json.JSONDecodeError, OSError):
            data = []
    data.append({
        "question": question,
        "answer": answer,
        "feedback": feedback,
        "timestamp": datetime.now().isoformat(),
    })
    FEEDBACK_FILE.write_text(
        json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8"
    )


# ==================================================
# 5. COVERAGE VERDICT
# ==================================================

def get_coverage_verdict(result):
    answer = result.get("answer", "")
    answer_lower = answer.lower()

    if (
        "i don't know" in answer_lower
        or "i do not know" in answer_lower
        or "not provide enough information" in answer_lower
        or not answer.strip()
    ):
        return (None, "")

    exclusion_terms = [
        "not covered", "excluded from", "not eligible",
        "exclusion list", "cannot be availed",
        "out-patient care", "outpatient", "cosmetic",
        "vaccine", "vaccination", "drug rehabilitation",
    ]
    approval_terms = [
        "pre-authoris", "pre authoris", "prior approval",
        "pre-auth", "mandatory approval",
        "approval required", "approval must be taken",
    ]

    if any(term in answer_lower for term in exclusion_terms):
        return (
            "Not covered",
            "The answer references exclusions or treatments not covered under PM-JAY. Confirm with an authorised hospital.",
        )
    if any(term in answer_lower for term in approval_terms):
        return (
            "Needs pre-approval",
            "The answer indicates that prior authorisation is required before treatment can be provided.",
        )
    return (
        "Covered",
        "The answer references treatments included under PM-JAY. Confirm coverage details with an empanelled hospital.",
    )


def display_verdict(verdict, reason):
    if verdict is None:
        return
    if verdict == "Covered":
        st.success("Coverage Status: Covered")
    elif verdict == "Not covered":
        st.error("Coverage Status: Not covered")
    else:
        st.warning("Coverage Status: Needs pre-approval")
    if reason:
        st.caption(reason)


# ==================================================
# 6. CITATIONS
# ==================================================

def display_citations(citations):
    if not citations:
        return
    with st.expander("View Sources and Citations"):
        for citation in citations:
            doc  = citation.get("document", "Healthcare document")
            page = citation.get("page", "")
            src  = citation.get("source", "")
            text = citation.get("text", "")
            cid  = citation.get("citation_id", "")

            st.markdown(f"**[{cid}] {doc}**")
            if page:
                st.caption(page)
            if text:
                st.markdown(
                    f"> {text[:400]}{'...' if len(text) > 400 else ''}",
                    help="Excerpt retrieved from the source document",
                )
            if src:
                if src.lower().endswith(".pdf") or "#page=" in src:
                    link_label = f"Open PDF — {page}" if page else "Open PDF"
                else:
                    link_label = "Open source document"
                st.markdown(f"[{link_label}]({src})")
            st.divider()


# ==================================================
# 7. DISPLAY CHAT MESSAGE
# ==================================================

def display_message(message, index):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message["role"] == "assistant":
            display_verdict(
                message.get("verdict"),
                message.get("verdict_reason", ""),
            )
            display_citations(message.get("citations", []))

            if message.get("approval_required"):
                st.info("The AI Agent is requesting human approval before continuing.")
                st.write(message.get("approval_request", ""))
                col1, col2 = st.columns(2)
                if col1.button("Approve", key=f"approve_{index}", use_container_width=True):
                    resume_agent(True, index)
                if col2.button("Reject", key=f"reject_{index}", use_container_width=True):
                    resume_agent(False, index)

            elif index not in st.session_state.feedback_given:
                col1, col2, _col3 = st.columns([1, 1, 5])
                if col1.button("+1", key=f"up_{index}"):
                    save_feedback(message.get("question", ""), message["content"], "positive")
                    st.session_state.feedback_given.append(index)
                    st.toast("Thank you for your feedback!")
                    st.rerun()
                if col2.button("-1", key=f"down_{index}"):
                    save_feedback(message.get("question", ""), message["content"], "negative")
                    st.session_state.feedback_given.append(index)
                    st.toast("Feedback saved!")
                    st.rerun()
            else:
                st.caption("Thank you for your feedback.")


# ==================================================
# 8. AGENT APPROVAL
# ==================================================

def resume_agent(approved, message_index):
    try:
        response = requests.post(
            f"{API_URL}/agent",
            json={"message": "", "thread_id": st.session_state.thread_id, "approval": approved},
            timeout=120,
        )
        response.raise_for_status()
        result = response.json()
        answer = result.get("answer") or json.dumps(result.get("result", result), indent=2, ensure_ascii=False)
        citations = result.get("citations", [])
        verdict, reason = get_coverage_verdict(result)
        st.session_state.messages[message_index]["content"] = answer
        st.session_state.messages[message_index]["citations"] = citations
        st.session_state.messages[message_index]["verdict"] = verdict
        st.session_state.messages[message_index]["verdict_reason"] = reason
        st.session_state.messages[message_index]["approval_required"] = False
        st.session_state.messages[message_index]["approval_request"] = ""
        st.rerun()
    except requests.exceptions.RequestException as error:
        st.error("Could not connect to the AI Agent.")
        st.caption(str(error))


# ==================================================
# 9. SIDEBAR
# ==================================================

with st.sidebar:
    st.markdown("# AyushmanSathi")
    st.caption("Healthcare Benefits Assistant")
    st.divider()

    st.markdown("### Navigation")
    nav_icons = {"Home": "Home", "AI Assistant": "AI Assistant", "About PM-JAY": "About PM-JAY", "Chat History": "Chat History"}
    pages = list(nav_icons.keys())
    selected_page = st.radio(
        "nav",
        pages,
        index=pages.index(st.session_state.page),
        label_visibility="collapsed",
    )
    st.session_state.page = selected_page

    st.divider()
    st.markdown("### Assistant Settings")
    st.session_state.mode = st.selectbox(
        "Assistant mode",
        ["RAG Question Answering", "AI Agent"],
        index=["RAG Question Answering", "AI Agent"].index(st.session_state.mode),
    )

    st.divider()
    st.markdown("### System")
    st.markdown(f"API: [{API_URL}]({API_URL})")
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.feedback_given = []
        st.session_state.pending_question = ""
        st.rerun()

    st.divider()
    st.markdown(
        """
        <div class="sidebar-badge">
            <div class="sidebar-badge-icon">&#10003;</div>
            <div class="sidebar-badge-text">
                Trusted healthcare<br>information for<br>patients and families.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==================================================
# 10. HOME PAGE
# ==================================================

if st.session_state.page == "Home":

    # Hero card
    st.markdown("""
    <div class="hero-card">
        <div class="hero-label">Welcome to</div>
        <div class="hero-title">AyushmanSathi</div>
        <div class="hero-subtitle">Your AI-powered healthcare benefits assistant.</div>
        <div class="hero-body">
            Get clear information about Ayushman Bharat PM-JAY, treatment coverage, eligibility and
            healthcare benefits. Ask questions in simple language and explore answers supported by official
            documents.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Service cards
    st.markdown('<div class="section-heading">Explore our services</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="medium")

    with col1:
        st.markdown("""
        <div class="svc-card">
            <h4>Treatment Coverage</h4>
            <p>Understand treatment coverage and applicable healthcare policy rules.</p>
        </div>""", unsafe_allow_html=True)

        st.markdown("""
        <div class="svc-card">
            <h4>Eligibility Guidance</h4>
            <p>Learn how to check eligibility and understand scheme requirements.</p>
        </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="svc-card">
            <h4>Scheme Information</h4>
            <p>Explore PM-JAY benefits, healthcare rules and scheme information.</p>
        </div>""", unsafe_allow_html=True)

        st.markdown("""
        <div class="svc-card">
            <h4>Trusted References</h4>
            <p>Review the healthcare documents used to support answers.</p>
        </div>""", unsafe_allow_html=True)

    # Popular questions
    st.markdown('<div class="section-heading">Popular questions</div>', unsafe_allow_html=True)

    pq_icons = ["+", "+", "+", "+"]
    pq_labels = [
        "What is Ayushman Bharat PM-JAY?",
        "Is cancer treatment covered under PM-JAY?",
        "How can I check my eligibility?",
        "What healthcare benefits are available?",
    ]

    r1c1, r1c2 = st.columns(2, gap="medium")
    r2c1, r2c2 = st.columns(2, gap="medium")
    pq_cols = [r1c1, r1c2, r2c1, r2c2]

    for i, label in enumerate(pq_labels):
        with pq_cols[i]:
            if st.button(label, key=f"pq_{i}", use_container_width=True):
                st.session_state.pending_question = label
                st.session_state.page = "AI Assistant"
                st.rerun()


# ==================================================
# 11. AI ASSISTANT PAGE
# ==================================================

elif st.session_state.page == "AI Assistant":

    st.markdown('<div class="page-heading">AI Healthcare Assistant</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-sub">Ask questions about PM-JAY, treatment coverage and healthcare benefits.</div>',
        unsafe_allow_html=True,
    )

    if not st.session_state.messages:
        st.info("Hello! I am AyushmanSathi. How can I help you today?")

    for index, message in enumerate(st.session_state.messages):
        display_message(message, index)

    question = st.chat_input("Type your healthcare question here...")

    if st.session_state.pending_question:
        question = st.session_state.pending_question
        st.session_state.pending_question = ""

    if question:
        st.session_state.messages.append({"role": "user", "content": question})

        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"), st.spinner("AyushmanSathi is preparing your answer..."):
            try:
                if st.session_state.mode == "RAG Question Answering":
                    response = requests.post(
                        f"{API_URL}/ask",
                        json={"question": question, "top_k": 5},
                        timeout=120,
                    )
                else:
                    response = requests.post(
                        f"{API_URL}/agent",
                        json={"message": question, "thread_id": st.session_state.thread_id},
                        timeout=120,
                    )

                response.raise_for_status()
                result = response.json()

                if st.session_state.mode == "RAG Question Answering":
                    answer = result.get("answer", "No answer was returned.")
                else:
                    if result.get("status") == "approval_required":
                        answer = "Your request requires human approval before the AI Agent can continue."
                    else:
                        answer = result.get("answer") or json.dumps(
                            result.get("result", result), indent=2, ensure_ascii=False
                        )

                citations = result.get("citations", [])
                verdict, reason = get_coverage_verdict(result)
                approval_required = (
                    st.session_state.mode == "AI Agent"
                    and result.get("status") == "approval_required"
                )
                approval_request = result.get("approval_request", "")

                st.markdown(answer)
                display_verdict(verdict, reason)
                display_citations(citations)

                if approval_required:
                    st.info("The AI Agent needs your approval before continuing.")
                    st.write(approval_request)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "question": question,
                    "citations": citations,
                    "verdict": verdict,
                    "verdict_reason": reason,
                    "approval_required": approval_required,
                    "approval_request": approval_request,
                })

                message_index = len(st.session_state.messages) - 1

                if not approval_required:
                    col1, col2, _col3 = st.columns([1, 1, 5])
                    if col1.button("+1", key=f"new_up_{message_index}"):
                        save_feedback(question, answer, "positive")
                        st.session_state.feedback_given.append(message_index)
                        st.toast("Thank you for your feedback!")
                        st.rerun()
                    if col2.button("-1", key=f"new_down_{message_index}"):
                        save_feedback(question, answer, "negative")
                        st.session_state.feedback_given.append(message_index)
                        st.toast("Feedback saved!")
                        st.rerun()

            except requests.exceptions.RequestException as error:
                st.error("Could not connect to AyushmanSathi API. Please check whether FastAPI is running.")
                st.caption(str(error))
            except (ValueError, KeyError, TypeError) as error:
                st.error("The API returned an unexpected response.")
                st.caption(str(error))


# ==================================================
# 12. ABOUT PM-JAY PAGE
# ==================================================

elif st.session_state.page == "About PM-JAY":

    st.markdown('<div class="page-heading">About PM-JAY</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-sub">Learn about Ayushman Bharat and healthcare benefits.</div>',
        unsafe_allow_html=True,
    )

    st.markdown("""
    <div class="about-card">
        <h2>Ayushman Bharat – PM-JAY</h2>
        <p>
        Pradhan Mantri Jan Arogya Yojana is a government healthcare scheme that provides
        hospitalisation benefits to eligible beneficiaries, subject to applicable scheme rules.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.info("Use the AI Assistant to ask questions about scheme benefits, eligibility and healthcare rules.")

    if st.button("Ask AyushmanSathi", use_container_width=True):
        st.session_state.page = "AI Assistant"
        st.rerun()


# ==================================================
# 13. CHAT HISTORY PAGE
# ==================================================

elif st.session_state.page == "Chat History":

    st.markdown('<div class="page-heading">Chat History</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-sub">Review your conversations from this session.</div>',
        unsafe_allow_html=True,
    )

    user_messages = [
        (index, message)
        for index, message in enumerate(st.session_state.messages)
        if message["role"] == "user"
    ]

    if not user_messages:
        st.info("No conversations yet. Start by asking a question.")
    else:
        for index, message in user_messages:
            with st.expander(f"Question {index + 1}: {message['content'][:70]}"):
                st.write("**Your question:**")
                st.write(message["content"])

                if index + 1 < len(st.session_state.messages):
                    answer_message = st.session_state.messages[index + 1]
                    if answer_message["role"] == "assistant":
                        st.write("**AyushmanSathi's answer:**")
                        st.markdown(answer_message["content"])
                        display_verdict(
                            answer_message.get("verdict"),
                            answer_message.get("verdict_reason", ""),
                        )
                        display_citations(answer_message.get("citations", []))


# ==================================================
# 14. FOOTER
# ==================================================

st.divider()
st.caption("AyushmanSathi | AI-Powered Healthcare Assistant")
st.caption(
    "This application provides informational guidance only. "
    "It does not provide official coverage approval or medical diagnosis. "
    "Always verify treatment decisions with an authorised hospital or the relevant government authority."
)
