import os
import json
from datetime import datetime
from pathlib import Path

import requests
import streamlit as st

# ==================================================
# 1. CONFIGURATION
# ==================================================

API_URL = os.getenv("API_URL", "http://127.0.0.1:8001")

FEEDBACK_FILE = Path(__file__).resolve().parent / "feedback.json"

st.set_page_config(
    page_title="AyushmanSathi | Healthcare Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================================================
# 2. CUSTOM DESIGN
# ==================================================

st.markdown("""
<style>
    /* Reduce the empty space above the page content */
    .block-container {
        padding-top: 0.8rem !important;
        padding-bottom: 1.5rem !important;
        max-width: 1100px;
    }

    /* Consistent text appearance */
    .stApp {
        background: #F5F8F8;
        color: #29464B;
        font-family: Arial, sans-serif;
    }

    p, [data-testid="stMarkdownContainer"] p {
        color: #526D70;
        font-size: 14px;
        line-height: 1.6;
    }

    h1, h2, h3, h4 {
        color: #153B43;
        line-height: 1.3;
    }

    [data-testid="stSidebar"] {
        background: #FFFFFF;
        border-right: 1px solid #E5ECEA;
    }

    [data-testid="stSidebar"] h1 {
        color: #087F70;
    }

    .main-heading {
        color: #153B43;
        font-size: 30px;
        font-weight: 700;
        line-height: 1.2;
        margin-top: 0;
        margin-bottom: 6px;
    }

    .sub-heading {
        color: #647A80;
        font-size: 14px;
        line-height: 1.5;
        margin-top: 0;
        margin-bottom: 20px;
    }

    .welcome-card {
        background: linear-gradient(120deg, #E1F3EC, #F0F8F5);
        border: 1px solid #D5EAE2;
        border-radius: 16px;
        padding: 24px;
        margin-top: 0;
        margin-bottom: 22px;
    }

    .welcome-card h2 {
        color: #153B43;
        font-size: 23px;
        line-height: 1.3;
        margin-top: 0;
        margin-bottom: 10px;
    }

    .welcome-card p {
        color: #526D70;
        font-size: 14px;
        line-height: 1.65;
    }

    .feature-card {
        background: #FFFFFF;
        border: 1px solid #E2EBE9;
        border-radius: 14px;
        padding: 20px;
        min-height: 135px;
    }

    .feature-card h4 {
        color: #153B43;
        font-size: 16px;
        line-height: 1.35;
        margin-top: 0;
        margin-bottom: 8px;
    }

    .feature-card p {
        color: #647A80;
        font-size: 13px;
        line-height: 1.6;
    }

    .section-heading {
        color: #153B43;
        font-size: 21px;
        font-weight: 700;
        margin-top: 20px;
        margin-bottom: 12px;
    }

    div.stButton > button {
        border-radius: 9px;
        min-height: 40px;
        border: 1px solid #D8E7E2;
    }

    [data-testid="stChatMessage"] {
        background: #FFFFFF;
        border: 1px solid #E7EEEC;
        border-radius: 12px;
        padding: 15px;
    }

    [data-testid="stChatInput"] {
        background: #FFFFFF;
    }

    footer {
        visibility: hidden;
    }
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
    "pending_approval": None
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ==================================================
# 4. FEEDBACK STORAGE
# ==================================================

def save_feedback(question, answer, feedback):

    FEEDBACK_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    data = []

    if FEEDBACK_FILE.exists():
        try:
            data = json.loads(
                FEEDBACK_FILE.read_text(encoding="utf-8")
            )

            if not isinstance(data, list):
                data = []

        except (json.JSONDecodeError, OSError):
            data = []

    data.append({
        "question": question,
        "answer": answer,
        "feedback": feedback,
        "timestamp": datetime.now().isoformat()
    })

    FEEDBACK_FILE.write_text(
        json.dumps(data, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )


# ==================================================
# 5. COVERAGE VERDICT
# ==================================================

def get_coverage_verdict(result):

    allowed_statuses = [
        "Covered",
        "Not covered",
        "Needs pre-approval"
    ]

    # Prefer an explicit backend verdict.
    backend_status = result.get("coverage_status")

    if backend_status in allowed_statuses:

        return (
            backend_status,
            result.get(
                "coverage_reason",
                "Verdict supplied by the healthcare policy service."
            )
        )

    # Otherwise inspect actual cited rule text, if supplied.
    cited_rules = result.get("cited_rules", [])

    if not cited_rules:
        return (
            "Needs pre-approval",
            (
                "The actual cited policy text is unavailable. "
                "Please confirm the treatment with an authorised hospital."
            )
        )

    rule_text = " ".join(
        str(rule.get("text", "")).lower()
        for rule in cited_rules
        if isinstance(rule, dict)
    )

    exclusion_terms = [
        "not covered",
        "excluded from the scheme",
        "shall not be liable",
        "excluded treatment"
    ]

    approval_terms = [
        "pre-authorization is required",
        "prior approval is required",
        "pre authorisation is required",
        "pre-authorization required"
    ]

    if any(term in rule_text for term in exclusion_terms):

        return (
            "Not covered",
            (
                "The cited policy contains exclusion-related wording. "
                "Confirm that the exclusion applies to this exact treatment."
            )
        )

    if any(term in rule_text for term in approval_terms):

        return (
            "Needs pre-approval",
            (
                "The cited policy indicates that prior authorisation "
                "is required."
            )
        )

    # Do not infer coverage from general policy information.
    return (
        "Needs pre-approval",
        (
            "The cited rules do not establish a definite coverage "
            "decision for this specific treatment."
        )
    )


def display_verdict(verdict, reason):

    if verdict == "Covered":
        st.success("✓ Coverage Status: Covered")

    elif verdict == "Not covered":
        st.error("✕ Coverage Status: Not covered")

    else:
        st.warning("⚠ Coverage Status: Needs pre-approval")

    st.caption(reason)


# ==================================================
# 6. CITATIONS
# ==================================================

def display_citations(citations):

    if not citations:
        st.caption("No source citations were returned.")
        return

    with st.expander("📚 View Sources and Citations"):

        for citation in citations:

            st.markdown(
                f"**{citation.get('document', 'Healthcare document')}**"
            )

            st.write(
                "Page:",
                citation.get("page", "Not specified")
            )

            if citation.get("source"):
                st.markdown(
                    f"[Open source document]({citation['source']})"
                )

            st.divider()


# ==================================================
# 7. DISPLAY CHAT MESSAGE
# ==================================================

def display_message(message, index):

    with st.chat_message(message["role"]):

        st.write(message["content"])

        if message["role"] == "assistant":

            display_verdict(
                message.get("verdict", "Needs pre-approval"),
                message.get("verdict_reason", "")
            )

            display_citations(
                message.get("citations", [])
            )

            # Human approval controls for agent responses.
            if message.get("approval_required"):

                st.info(
                    "The AI Agent is requesting human approval "
                    "before continuing."
                )

                st.write(message.get("approval_request", ""))

                col1, col2 = st.columns(2)

                if col1.button(
                    "Approve",
                    key=f"approve_{index}",
                    use_container_width=True
                ):
                    resume_agent(True, index)

                if col2.button(
                    "Reject",
                    key=f"reject_{index}",
                    use_container_width=True
                ):
                    resume_agent(False, index)

            # Feedback controls.
            elif index not in st.session_state.feedback_given:

                col1, col2, _col3 = st.columns([1, 1, 5])

                if col1.button("👍", key=f"up_{index}"):

                    save_feedback(
                        message.get("question", ""),
                        message["content"],
                        "positive"
                    )

                    st.session_state.feedback_given.append(index)
                    st.toast("Thank you for your feedback!")
                    st.rerun()

                if col2.button("👎", key=f"down_{index}"):

                    save_feedback(
                        message.get("question", ""),
                        message["content"],
                        "negative"
                    )

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
            json={
                "message": "",
                "thread_id": st.session_state.thread_id,
                "approval": approved
            },
            timeout=120
        )

        response.raise_for_status()
        result = response.json()

        answer = result.get("answer")

        if not answer:
            answer = json.dumps(
                result.get("result", result),
                indent=2,
                ensure_ascii=False
            )

        citations = result.get("citations", [])

        verdict, reason = get_coverage_verdict(result)

        # Update the original approval message.
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

    st.markdown("# 🏥 AyushmanSathi")
    st.caption("Healthcare Benefits Assistant")

    st.divider()

    st.markdown("### Navigation")

    pages = [
        "Home",
        "AI Assistant",
        "About PM-JAY",
        "Chat History"
    ]

    selected_page = st.radio(
        "Select a page",
        pages,
        index=pages.index(st.session_state.page),
        label_visibility="collapsed"
    )

    st.session_state.page = selected_page

    st.divider()

    st.markdown("### Assistant Settings")

    st.session_state.mode = st.selectbox(
        "Assistant mode",
        [
            "RAG Question Answering",
            "AI Agent"
        ],
        index=[
            "RAG Question Answering",
            "AI Agent"
        ].index(st.session_state.mode)
    )

    st.divider()

    st.markdown("### System")

    st.caption("API: " + API_URL)

    if st.button("Clear Chat", use_container_width=True):

        st.session_state.messages = []
        st.session_state.feedback_given = []
        st.session_state.pending_question = ""
        st.rerun()

    st.divider()

    st.caption(
        "Simple healthcare information for patients "
        "and their families."
    )


# ==================================================
# 10. HOME PAGE
# ==================================================

if st.session_state.page == "Home":

    st.markdown(
        '<div class="main-heading">Welcome to AyushmanSathi</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sub-heading">'
        'Your AI-powered healthcare benefits assistant.'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="welcome-card">
        <h2>Healthcare guidance, made simple.</h2>
        <p>
        Get clear information about Ayushman Bharat PM-JAY,
        treatment coverage, eligibility and healthcare benefits.
        Ask questions in simple language and explore answers
        supported by healthcare documents.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="section-heading">Explore our services</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("""
        <div class="feature-card">
            <h4>🛡️ Treatment Coverage</h4>
            <p>
            Understand treatment coverage and
            applicable healthcare policy rules.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
        <div class="feature-card">
            <h4>📋 Eligibility Guidance</h4>
            <p>
            Learn how to check eligibility and
            understand scheme requirements.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:

        st.markdown("""
        <div class="feature-card">
            <h4>📖 Scheme Information</h4>
            <p>
            Explore PM-JAY benefits, healthcare
            rules and scheme information.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
        <div class="feature-card">
            <h4>📚 Trusted References</h4>
            <p>
            Review the healthcare documents
            used to support answers.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(
        '<div class="section-heading">Popular questions</div>',
        unsafe_allow_html=True
    )

    questions = [
        "What is Ayushman Bharat PM-JAY?",
        "Is cancer treatment covered under PM-JAY?",
        "How can I check my eligibility?",
        "What healthcare benefits are available?"
    ]

    for question in questions:

        if st.button(question, use_container_width=True):

            st.session_state.pending_question = question
            st.session_state.page = "AI Assistant"
            st.rerun()

    st.info(
        "Choose AI Assistant from the sidebar to start "
        "a conversation."
    )


# ==================================================
# 11. AI ASSISTANT PAGE
# ==================================================

elif st.session_state.page == "AI Assistant":

    st.markdown(
        '<div class="main-heading">AI Healthcare Assistant</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sub-heading">'
        'Ask questions about PM-JAY, treatment coverage '
        'and healthcare benefits.'
        '</div>',
        unsafe_allow_html=True
    )

    if not st.session_state.messages:

        st.info(
            "Hello! I am AyushmanSathi. "
            "How can I help you today?"
        )

    # Display conversation history.
    for index, message in enumerate(st.session_state.messages):
        display_message(message, index)

    question = st.chat_input(
        "Type your healthcare question here..."
    )

    # Question selected from the home page.
    if st.session_state.pending_question:

        question = st.session_state.pending_question
        st.session_state.pending_question = ""

    if question:

        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"), st.spinner(
            "AyushmanSathi is preparing your answer..."
        ):

            try:

                if st.session_state.mode == "RAG Question Answering":

                    response = requests.post(
                        f"{API_URL}/ask",
                        json={
                            "question": question,
                            "top_k": 5
                        },
                        timeout=120
                    )

                else:

                    response = requests.post(
                        f"{API_URL}/agent",
                        json={
                            "message": question,
                            "thread_id": st.session_state.thread_id
                        },
                        timeout=120
                    )

                response.raise_for_status()

                result = response.json()

                # Extract answer.
                if st.session_state.mode == "RAG Question Answering":

                    answer = result.get(
                        "answer",
                        "No answer was returned."
                    )

                else:

                    if result.get("status") == "approval_required":

                        answer = (
                            "Your request requires human approval "
                            "before the AI Agent can continue."
                        )

                    else:

                        answer = result.get("answer")

                        if not answer:

                            answer = json.dumps(
                                result.get("result", result),
                                indent=2,
                                ensure_ascii=False
                            )

                citations = result.get("citations", [])

                verdict, reason = get_coverage_verdict(result)

                approval_required = (
                    st.session_state.mode == "AI Agent"
                    and result.get("status") == "approval_required"
                )

                approval_request = result.get(
                    "approval_request", ""
                )

                # Display answer.
                st.write(answer)

                display_verdict(verdict, reason)

                display_citations(citations)

                if approval_required:

                    st.info(
                        "The AI Agent needs your approval "
                        "before continuing."
                    )

                    st.write(approval_request)

                # Store answer in session history.
                message_index = len(st.session_state.messages)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "question": question,
                    "citations": citations,
                    "verdict": verdict,
                    "verdict_reason": reason,
                    "approval_required": approval_required,
                    "approval_request": approval_request
                })

                # Feedback for the new answer.
                if not approval_required:

                    col1, col2, _col3 = st.columns([1, 1, 5])

                    if col1.button(
                        "👍",
                        key=f"new_up_{message_index}"
                    ):

                        save_feedback(
                            question,
                            answer,
                            "positive"
                        )

                        st.session_state.feedback_given.append(
                            message_index
                        )

                        st.toast("Thank you for your feedback!")
                        st.rerun()

                    if col2.button(
                        "👎",
                        key=f"new_down_{message_index}"
                    ):

                        save_feedback(
                            question,
                            answer,
                            "negative"
                        )

                        st.session_state.feedback_given.append(
                            message_index
                        )

                        st.toast("Feedback saved!")
                        st.rerun()

            except requests.exceptions.RequestException as error:

                st.error(
                    "Could not connect to AyushmanSathi API. "
                    "Please check whether FastAPI is running."
                )

                st.caption(str(error))

            except (ValueError, KeyError, TypeError) as error:

                st.error("The API returned an unexpected response.")
                st.caption(str(error))


# ==================================================
# 12. ABOUT PM-JAY PAGE
# ==================================================

elif st.session_state.page == "About PM-JAY":

    st.markdown(
        '<div class="main-heading">About PM-JAY</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sub-heading">'
        'Learn about Ayushman Bharat and healthcare benefits.'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="welcome-card">
        <h2>Ayushman Bharat – PM-JAY</h2>
        <p>
        Pradhan Mantri Jan Arogya Yojana is a government
        healthcare scheme that provides hospitalisation
        benefits to eligible beneficiaries, subject to
        applicable scheme rules.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.info(
        "Use the AI Assistant to ask questions about scheme "
        "benefits, eligibility and healthcare rules."
    )

    if st.button("Ask AyushmanSathi", use_container_width=True):

        st.session_state.page = "AI Assistant"
        st.rerun()


# ==================================================
# 13. CHAT HISTORY PAGE
# ==================================================

elif st.session_state.page == "Chat History":

    st.markdown(
        '<div class="main-heading">Chat History</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sub-heading">'
        'Review your conversations from this session.'
        '</div>',
        unsafe_allow_html=True
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

            with st.expander(
                f"Question {index + 1}: {message['content'][:70]}"
            ):

                st.write("**Your question:**")
                st.write(message["content"])

                if index + 1 < len(st.session_state.messages):

                    answer_message = st.session_state.messages[index + 1]

                    if answer_message["role"] == "assistant":

                        st.write("**AyushmanSathi's answer:**")
                        st.write(answer_message["content"])

                        display_verdict(
                            answer_message.get(
                                "verdict",
                                "Needs pre-approval"
                            ),
                            answer_message.get("verdict_reason", "")
                        )

                        display_citations(
                            answer_message.get("citations", [])
                        )


# ==================================================
# 14. FOOTER
# ==================================================

st.divider()

st.caption(
    "AyushmanSathi | AI-Powered Healthcare Assistant"
)

st.caption(
    "This application provides informational guidance only. "
    "It does not provide official coverage approval or medical "
    "diagnosis. Always verify treatment decisions with an "
    "authorised hospital or the relevant government authority."
)
