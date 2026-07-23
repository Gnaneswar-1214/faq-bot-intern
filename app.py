import os
import streamlit as st
import numpy as np
from dotenv import load_dotenv

load_dotenv()

from src.extract import extract_text_from_file
from src.chunk import chunk_text
from src.embed import EmbeddingManager
from src.retrieve import retrieve_top_k
from src.generate import generate_answer

# ---------------- CONFIGURATION & THEME ----------------
st.set_page_config(
    page_title="RAG FAQ Bot - Premium Suite",
    page_icon="🤖",
    layout="wide"
)

# Custom Glassmorphic Dark Theme injection
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

/* Apply modern Outfit font to entire Streamlit App */
html, body, [class*="css"], .stMarkdown {
    font-family: 'Outfit', sans-serif !important;
}

/* App Header gradient title */
.gradient-text {
    background: linear-gradient(90deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.8rem;
    font-weight: 800;
    margin-bottom: 0.2rem;
}

.sub-text {
    color: #94a3b8;
    font-size: 1.1rem;
    margin-bottom: 1.5rem;
}

/* Sidebar Styling */
section[data-testid="stSidebar"] {
    background-color: #0d0e15 !important;
    border-right: 1px solid #1e293b !important;
}

/* Style the file uploader */
div[data-testid="stFileUploader"] {
    border: 2px dashed #4f46e5;
    border-radius: 12px;
    background-color: #111322;
    padding: 1rem;
    transition: all 0.3s ease-in-out;
}
div[data-testid="stFileUploader"]:hover {
    border-color: #ec4899;
    background-color: #171b30;
}

/* Custom card container for stats and metrics */
.metrics-container {
    background: rgba(17, 24, 39, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 1.25rem;
    backdrop-filter: blur(12px);
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    margin-bottom: 1rem;
}

/* Streamlit buttons custom styling */
button[kind="secondary"] {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
    color: white !important;
    border: none !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    padding: 0.5rem 1rem !important;
    transition: all 0.2s ease-in-out !important;
}
button[kind="secondary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4) !important;
}

/* Status Indicator Box */
.status-badge {
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
    display: inline-block;
    border: 1px solid currentColor;
    margin-top: 5px;
}

/* Custom styled chat messages */
div[data-testid="stChatMessage"] {
    background-color: #111827 !important;
    border: 1px solid #1f2937 !important;
    border-radius: 16px !important;
    padding: 1.2rem !important;
    margin-bottom: 0.8rem !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
}
div[data-testid="stChatMessage"]:nth-child(odd) {
    background-color: #1e1b4b !important;
    border-color: #312e81 !important;
}

</style>
""", unsafe_allow_html=True)


# Initialize session state variables
if "embedding_manager" not in st.session_state:
    st.session_state.embedding_manager = None

if "document_data" not in st.session_state:
    st.session_state.document_data = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ---------------- SIDEBAR: CONFIGURATION ----------------
st.sidebar.title("🤖 FAQ Bot Configuration")
st.sidebar.markdown("Configure your document ingestion and LLM execution parameters.")
st.sidebar.markdown("---")

# Supported formats: PDF, TXT, DOCX, MD
uploaded_file = st.sidebar.file_uploader(
    "Upload Document (PDF, TXT, DOCX, MD)",
    type=["pdf", "txt", "docx", "md"],
    help="Upload any PDF, Plain Text, Word Doc, or Markdown file to index and query."
)

st.sidebar.markdown("### ⚙️ RAG Hyperparameters")
threshold = st.sidebar.slider(
    "Similarity Threshold",
    min_value=0.0,
    max_value=1.0,
    value=float(os.getenv("SIMILARITY_THRESHOLD", 0.25)),
    step=0.05,
    help="Minimum cosine similarity required for a chunk to be considered relevant context."
)

top_k = st.sidebar.slider(
    "Top-K Chunks to Retrieve",
    min_value=1,
    max_value=10,
    value=int(os.getenv("TOP_K", 3)),
    step=1,
    help="Number of highly matching document chunks to retrieve."
)

st.sidebar.markdown("### 🔑 LLM API Settings")
provider = st.sidebar.selectbox(
    "LLM Provider",
    options=["auto", "gemini", "openai", "mock"],
    index=0
)

# Custom Model Selection
if provider == "gemini":
    model_options = ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
elif provider == "openai":
    model_options = ["gpt-3.5-turbo", "gpt-4o", "gpt-4-turbo", "gpt-4"]
elif provider == "auto":
    model_options = ["auto"]
else:
    model_options = ["mock"]

model = st.sidebar.selectbox(
    "LLM Model",
    options=model_options,
    index=0,
    help="Select the model target. Select 'auto' to use provider defaults."
)

api_key_input = st.sidebar.text_input(
    "API Key (Optional override)",
    type="password"
)

if api_key_input:
    if provider == "openai":
        os.environ["OPENAI_API_KEY"] = api_key_input
    else:
        os.environ["GEMINI_API_KEY"] = api_key_input

# API Status Badge calculation
gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
openai_key = os.getenv("OPENAI_API_KEY")

st.sidebar.markdown("### 📡 API Status")
if provider == "gemini" and gemini_key:
    st.sidebar.markdown('<div class="status-badge" style="color: #10B981;">🟢 Gemini API Active</div>', unsafe_allow_html=True)
elif provider == "openai" and openai_key:
    st.sidebar.markdown('<div class="status-badge" style="color: #10B981;">🟢 OpenAI API Active</div>', unsafe_allow_html=True)
elif provider == "auto" and (gemini_key or openai_key):
    active_prov = "Gemini" if gemini_key else "OpenAI"
    st.sidebar.markdown(f'<div class="status-badge" style="color: #10B981;">🟢 {active_prov} Active (Auto)</div>', unsafe_allow_html=True)
elif provider == "mock":
    st.sidebar.markdown('<div class="status-badge" style="color: #F59E0B;">🟡 Offline Mock Mode</div>', unsafe_allow_html=True)
else:
    st.sidebar.markdown('<div class="status-badge" style="color: #EF4444;">🔴 API Key Missing (Demo Fallback)</div>', unsafe_allow_html=True)

st.sidebar.markdown("---")
if st.sidebar.button("🧹 Clear Session & History", use_container_width=True):
    st.session_state.document_data = None
    st.session_state.chat_history = []
    st.rerun()


# ---------------- CORE LOGIC: FILE INGESTION ----------------
if uploaded_file is not None:
    current_filename = uploaded_file.name
    if (
        st.session_state.document_data is None or
        st.session_state.document_data["filename"] != current_filename
    ):
        with st.spinner(f"Extracting & Indexing '{current_filename}'..."):
            try:
                raw_text = extract_text_from_file(uploaded_file, current_filename)
                chunk_size = int(os.getenv("CHUNK_SIZE", 250))
                overlap = int(os.getenv("CHUNK_OVERLAP", 50))
                chunks = chunk_text(raw_text, chunk_size=chunk_size, overlap=overlap)
                
                if st.session_state.embedding_manager is None:
                    st.session_state.embedding_manager = EmbeddingManager()
                
                embeddings = st.session_state.embedding_manager.fit_and_embed_chunks(chunks)

                st.session_state.document_data = {
                    "filename": current_filename,
                    "text": raw_text,
                    "chunks": chunks,
                    "embeddings": embeddings
                }
                st.session_state.chat_history = []
                st.toast(f"Successfully indexed {len(chunks)} chunks!", icon="✅")
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")


# ---------------- MAIN APP LAYOUT ----------------
st.markdown('<div class="gradient-text">🤖 Single-Document FAQ RAG Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">Upload a document to index and query it with natural language under a fully grounded context.</div>', unsafe_allow_html=True)

doc = st.session_state.document_data

if doc is None:
    # Empty State Display
    st.info("👈 Please upload a PDF, TXT, DOCX, or MD file using the sidebar to begin.")
    
    st.markdown("### 📄 Or start with a Sample Document")
    if st.button("Load Sample Policy Document"):
        sample_path = "data/sample_docs/sample_policy.txt"
        if os.path.exists(sample_path):
            with open(sample_path, "r", encoding="utf-8") as f:
                content = f.read()
            chunks = chunk_text(content, chunk_size=250, overlap=50)
            if st.session_state.embedding_manager is None:
                st.session_state.embedding_manager = EmbeddingManager()
            embeddings = st.session_state.embedding_manager.fit_and_embed_chunks(chunks)
            
            st.session_state.document_data = {
                "filename": "sample_policy.txt",
                "text": content,
                "chunks": chunks,
                "embeddings": embeddings
            }
            st.rerun()
else:
    # Main Tabs
    tab1, tab2 = st.tabs(["💬 Chat Assistant", "📄 Document & Chunk Inspector"])
    
    with tab1:
        # Chat History Container
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if "retrieved_results" in message and message["retrieved_results"]:
                    with st.expander("🔍 View Retrieved Source Chunks"):
                        for item in message["retrieved_results"]:
                            c = item["chunk"]
                            score = item["score"]
                            color_score = "#10B981" if score >= threshold else "#F59E0B"
                            st.markdown(f"**Chunk #{c['id']}** | *Similarity Score: <span style='color:{color_score}; font-weight:bold;'>{score:.4f}</span>*", unsafe_allow_html=True)
                            st.caption(c["text"])
                            st.divider()

    with tab2:
        # Document Stats Card
        st.markdown(f"""
        <div class="metrics-container">
            <h4 style="margin-top:0px; color:#a855f7;">📊 Workspace Metadata</h4>
            <table style="width:100%; border-collapse:collapse; color:#cbd5e1;">
                <tr>
                    <td style="padding:8px 0; font-weight:bold; width:30%;">Active Document:</td>
                    <td style="padding:8px 0; color:#3b82f6;">{doc["filename"]}</td>
                </tr>
                <tr>
                    <td style="padding:8px 0; font-weight:bold;">Total Chars:</td>
                    <td style="padding:8px 0;">{len(doc["text"]):,} characters</td>
                </tr>
                <tr>
                    <td style="padding:8px 0; font-weight:bold;">Total Chunks:</td>
                    <td style="padding:8px 0;">{len(doc["chunks"])} segments</td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 📝 Extracted Text Preview")
        preview_length = 5000
        preview_text = doc["text"][:preview_length]
        if len(doc["text"]) > preview_length:
            preview_text += f"\n\n... [TRUNCATED {len(doc['text']) - preview_length:,} CHARS FOR PERFORMANCE]"
        st.text_area("Extracted Text", preview_text, height=300, disabled=True)
        
        st.markdown("### 🧩 Generated Text Chunks")
        for chunk in doc["chunks"]:
            with st.expander(f"Chunk #{chunk['id']} (Words: {chunk['word_count']}, Chars: {chunk['char_count']})"):
                st.write(chunk["text"])

    # Chat Input handler (outside of tabs at bottom for best Streamlit lifecycle behavior)
    if user_question := st.chat_input("Ask a question about the document..."):
        # Instantly append user question so it renders
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        
        with tab1:
            with st.chat_message("user"):
                st.markdown(user_question)
            
            with st.chat_message("assistant"):
                with st.spinner("Retrieving relevant context & generating grounded answer..."):
                    # 1. Embed query
                    query_vec = st.session_state.embedding_manager.embed_query(user_question)

                    # 2. Retrieve top matching chunks
                    retrieval = retrieve_top_k(
                        query_vec=query_vec,
                        chunk_vecs=doc["embeddings"],
                        chunks=doc["chunks"],
                        top_k=top_k,
                        threshold=threshold
                    )

                    # 3. Generate grounded answer
                    answer = generate_answer(
                        query=user_question,
                        retrieved_results=retrieval["results"],
                        is_relevant=retrieval["is_relevant"],
                        provider=provider,
                        model=model
                    )

                    st.markdown(answer)
                    
                    if retrieval["results"]:
                        with st.expander("🔍 View Retrieved Source Chunks"):
                            for item in retrieval["results"]:
                                c = item["chunk"]
                                score = item["score"]
                                color_score = "#10B981" if score >= threshold else "#F59E0B"
                                st.markdown(f"**Chunk #{c['id']}** | *Similarity Score: <span style='color:{color_score}; font-weight:bold;'>{score:.4f}</span>*", unsafe_allow_html=True)
                                st.caption(c["text"])
                                st.divider()

        # Append assistant response to chat history
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": answer,
            "retrieved_results": retrieval["results"]
        })
        st.rerun()
