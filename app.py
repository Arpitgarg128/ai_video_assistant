import os
import tempfile
import streamlit as st
from dotenv import load_dotenv

from main import run_pipeline
from core.rag_engine import ask_question

load_dotenv()

st.set_page_config(
    page_title="AI Video Assistant",
    page_icon="🎥",
    layout="wide"
)

# -------------------------------
# Custom CSS
# -------------------------------

st.markdown("""
<style>

.main{
    padding-top:2rem;
}

.block{
    padding:18px;
    border-radius:12px;
    background:#f7f7f7;
    margin-bottom:15px;
}

.title{
    font-size:32px;
    font-weight:700;
    text-align:center;
    margin-bottom:20px;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------
# Header
# -------------------------------

st.markdown("<div class='title'>🎥 AI Video Meeting Assistant</div>",
unsafe_allow_html=True)

st.write(
    "Upload a meeting recording or paste a YouTube URL to generate "
    "summaries, action items, key decisions and chat with your meeting."
)

# -------------------------------
# Sidebar
# -------------------------------

st.sidebar.header("Input")

language = st.sidebar.selectbox(
    "Language",
    ["english", "hinglish"]
)

input_type = st.sidebar.radio(
    "Choose Source",
    ["YouTube URL", "Upload Video"]
)

source = None

if input_type == "YouTube URL":
    source = st.text_input("YouTube URL")

else:
    uploaded_file = st.file_uploader(
        "Upload video/audio",
        type=["mp4","mp3","wav","mkv","mov","m4a"]
    )

    if uploaded_file:

        temp = tempfile.NamedTemporaryFile(delete=False)

        temp.write(uploaded_file.read())

        source = temp.name

# -------------------------------
# Run
# -------------------------------

if st.button("🚀 Process"):

    if not source:
        st.warning("Please provide a source.")
        st.stop()

    progress = st.progress(0)

    status = st.empty()

    status.text("Downloading / Extracting Audio...")
    progress.progress(15)

    result = run_pipeline(source, language)

    progress.progress(100)

    status.success("Completed!")

    st.session_state.result = result
    st.session_state.chat = []

# -------------------------------
# Display Results
# -------------------------------

if "result" in st.session_state:

    result = st.session_state.result

    st.success("Processing Complete")

    st.header(result["title"])

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "📝 Summary",
            "📜 Transcript",
            "💬 Chat",
            "ℹ️ Details"
        ]
    )

    # ---------------- Summary ----------------

    with tab1:

        col1, col2 = st.columns(2)

        with col1:

            st.subheader("Summary")

            st.info(result["summary"])

            st.subheader("Action Items")

            st.success(result["action_items"])

        with col2:

            st.subheader("Key Decisions")

            st.warning(result["key_decisions"])

            st.subheader("Open Questions")

            st.error(result["open_questions"])

    # ---------------- Transcript ----------------

    with tab2:

        st.subheader("Transcript")

        st.text_area(
            "",
            result["transcript"],
            height=500
        )

    # ---------------- Chat ----------------

    with tab3:

        st.subheader("Chat with Meeting")

        if "chat" not in st.session_state:
            st.session_state.chat = []

        for role, message in st.session_state.chat:

            with st.chat_message(role):
                st.write(message)

        question = st.chat_input(
            "Ask something about the meeting..."
        )

        if question:

            st.session_state.chat.append(
                ("user", question)
            )

            with st.chat_message("user"):
                st.write(question)

            answer = ask_question(
                result["rag_chain"],
                question
            )

            with st.chat_message("assistant"):
                st.write(answer)

            st.session_state.chat.append(
                ("assistant", answer)
            )

    # ---------------- Details ----------------

    with tab4:

        st.metric(
            "Transcript Length",
            f"{len(result['transcript'].split())} words"
        )

        st.metric(
            "Summary Length",
            f"{len(result['summary'].split())} words"
        )

        st.download_button(
            "Download Transcript",
            result["transcript"],
            file_name="transcript.txt"
        )

        st.download_button(
            "Download Summary",
            result["summary"],
            file_name="summary.txt"
        )