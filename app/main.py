import streamlit as st
import os
import sys
from pathlib import Path

# Load environment variables first
from dotenv import load_dotenv
load_dotenv()

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from services.auth_service import AuthService
from services.chat_service import ChatService
from services.arxiv_service import ArXivService
from rag.retriever import RAGRetriever
from rag.chain import RAGChain
import json

# Page configuration
st.set_page_config(
    page_title="Research Paper Chatbot",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ✅ Initialize session state at the top only ONCE
DEFAULT_SESSION_KEYS = {
    "user_papers": [],
    "authenticated": False,
    "user_id": None,
    "chat_history": [],
    "arxiv_results": None,
    "show_success_messages": True
}

for key, val in DEFAULT_SESSION_KEYS.items():
    if key not in st.session_state:
        st.session_state[key] = val

# Initialize services
@st.cache_resource
def init_services():
    """Initialize all services with caching"""
    try:
        auth_service = AuthService()
        chat_service = ChatService()
        arxiv_service = ArXivService()
        retriever = RAGRetriever()
        rag_chain = RAGChain(retriever)
        return auth_service, chat_service, arxiv_service, rag_chain
    except Exception as e:
        st.error(f"Error initializing services: {str(e)}")
        st.error("Please check your .env file and ensure all required API keys are set.")
        return None, None, None, None

def main():
    # Initialize services
    auth_service, chat_service, arxiv_service, rag_chain = init_services()
    
    # Check if services initialized successfully
    if auth_service is None or chat_service is None or arxiv_service is None or rag_chain is None:
        st.error("Failed to initialize services. Please check your configuration.")
        st.stop()
    
    # Sidebar for authentication
    with st.sidebar:
        st.title("🔐 Authentication")
        
        if not st.session_state.authenticated:
            tab1, tab2 = st.tabs(["Login", "Sign Up"])
            
            with tab1:
                st.subheader("Login")
                email = st.text_input("Email", key="login_email")
                password = st.text_input("Password", type="password", key="login_password")
                
                if st.button("Login"):
                    if auth_service.login(email, password):
                        st.session_state.authenticated = True
                        st.session_state.user_id = email
                        st.success("Login successful!")
                    else:
                        st.error("Invalid credentials")
            
            with tab2:
                st.subheader("Sign Up")
                new_email = st.text_input("Email", key="signup_email")
                new_password = st.text_input("Password", type="password", key="signup_password")
                confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
                
                if st.button("Sign Up"):
                    if new_password != confirm_password:
                        st.error("Passwords don't match")
                    elif auth_service.signup(new_email, new_password):
                        st.success("Account created successfully! Please login.")
                    else:
                        st.error("Account creation failed")
        
        else:
            st.success(f"Welcome, {st.session_state.user_id}!")
            if st.button("Logout"):
                st.session_state.authenticated = False
                st.session_state.user_id = None
                st.session_state.chat_history = []
                st.session_state.user_papers = []
                st.session_state.arxiv_results = None
    
    # Main content area
    if st.session_state.authenticated:
        # Header
        st.title("📚 Research Paper Chatbot")
        st.markdown("Ask questions about your research papers and get AI-powered answers!")
        
        # Persona selection
        col1, col2, col3 = st.columns(3)
        with col1:
            persona = st.selectbox(
                "Choose your persona:",
                ["Student", "Professor", "General User"],
                help="This will customize the response style and depth"
            )
        
        with col2:
            # File upload
            uploaded_file = st.file_uploader(
                "Upload PDF Paper",
                type=['pdf'],
                help="Upload a research paper PDF to analyze"
            )
        
        with col3:
            # ArXiv search
            arxiv_query = st.text_input("Or search ArXiv by topic:", placeholder="e.g., machine learning")
            max_results = st.selectbox("Number of results:", [5, 10, 15, 20], index=0)
            search_button = st.button("🔍 Search ArXiv")
            if search_button and arxiv_query:
                with st.spinner("Searching ArXiv..."):
                    try:
                        papers = arxiv_service.search_papers(arxiv_query, max_results)
                        if papers:
                            st.session_state.arxiv_results = papers
                            st.success(f"Found {len(papers)} papers!")
                        else:
                            st.error("No papers found for this query.")
                    except Exception as e:
                        st.error(f"Error searching ArXiv: {str(e)}")
            elif search_button and not arxiv_query:
                st.warning("Please enter a search query.")
        
        # 📚 Display user's papers
        if st.session_state.user_papers:
            st.markdown("---")
            st.subheader("📚 Your Papers")
            st.markdown(f"You have **{len(st.session_state.user_papers)}** papers available for chat:")

            for i, paper in enumerate(st.session_state.user_papers):  # ✅ fixed indent
                status_icon = "⏳" if paper.get('needs_processing') else "✅"
                status_text = " (Processing Pending)" if paper.get('needs_processing') else " (Ready)"

                with st.expander(f"{status_icon} {paper['title']} ({paper['paper_id']}){status_text}"):
                    st.markdown(f"**Source:** {paper['source']}")
                    st.markdown(f"**Uploaded:** {paper['upload_date']}")

                    if paper.get('needs_processing'):
                        st.markdown("**Status:** ⏳ Will be processed when you ask questions")
                    else:
                        st.markdown("**Status:** ✅ Ready for chat")

                    if st.button(f"🗑️ Remove Paper {i+1}", key=f"remove_paper_{i}"):
                        st.session_state.user_papers.pop(i)
        
        # 📄 ArXiv results (fixed indent in col2)
        if 'arxiv_results' in st.session_state and st.session_state.arxiv_results:
            st.markdown("---")
            col1, col2 = st.columns([3, 1])
            with col1:
                st.subheader("📄 ArXiv Search Results")
            with col2:
                if st.button("🗑️ Clear Results"):
                    st.session_state.arxiv_results = None

            paper_tabs = st.tabs([f"Paper {i+1}" for i in range(len(st.session_state.arxiv_results))])

            for i, (tab, paper) in enumerate(zip(paper_tabs, st.session_state.arxiv_results)):
                with tab:
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        st.markdown(f"**{paper['title']}**")
                        st.markdown(f"**Authors:** {', '.join(paper['authors'])}")
                        st.markdown(f"**Published:** {paper['published']}")
                        st.markdown(f"**Categories:** {', '.join(paper['categories'])}")
                        if paper.get('doi'):
                            st.markdown(f"**DOI:** {paper['doi']}")
                        st.markdown("**Abstract:**")
                        st.markdown(paper['summary'][:500] + "..." if len(paper['summary']) > 500 else paper['summary'])

                    with col2:  # ✅ fixed indent
                        st.markdown("**Actions:**")
                        if st.button(f"📥 Add to Library", key=f"add_{i}"):
                            # Add paper to user's papers list without processing
                            paper_info = {
                                'paper_id': paper['id'],
                                'title': paper['title'],
                                'authors': paper['authors'],
                                'source': 'ArXiv',
                                'upload_date': paper['published'],
                                'arxiv_id': paper['id'],
                                'pdf_url': paper['pdf_url'],
                                'needs_processing': True
                            }
                            existing_papers = [p for p in st.session_state.user_papers if p.get('arxiv_id') == paper['id']]
                            if not existing_papers:
                                st.session_state.user_papers.append(paper_info)
                                st.success("✅ Paper added to your library!")
                                st.info("Paper will be processed when you ask questions about it.")
                            else:
                                st.warning("⚠️ This paper is already in your library!")

                        if st.button(f"🔗 View on ArXiv", key=f"view_{i}"):
                            st.markdown(f"[Open on ArXiv]({paper['pdf_url']})")
        
        # Process uploaded file
        if uploaded_file is not None:
            # Check if this file was already processed
            file_already_processed = any(p.get('filename') == uploaded_file.name for p in st.session_state.user_papers)
            
            if not file_already_processed:
                with st.spinner("Processing PDF..."):
                    # Save uploaded file temporarily
                    temp_path = f"temp_{uploaded_file.name}"
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Ingest the PDF
                    try:
                        from rag.ingest import PDFIngester
                        ingester = PDFIngester()
                        paper_id = ingester.ingest_pdf(temp_path, st.session_state.user_id)
                        
                        # Add paper to user's papers list
                        paper_info = {
                            'paper_id': paper_id,
                            'title': uploaded_file.name.replace('.pdf', ''),
                            'authors': ['Unknown'],
                            'source': 'Uploaded File',
                            'upload_date': 'Today',
                            'filename': uploaded_file.name
                        }
                        
                        st.session_state.user_papers.append(paper_info)
                        st.success(f"✅ Paper processed and added to your library!")
                        st.info(f"Paper ID: {paper_id}")
                        
                        # Clean up temp file
                        os.remove(temp_path)
                        
                    except Exception as e:
                        st.error(f"Error processing PDF: {str(e)}")
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
            else:
                st.warning("⚠️ This paper is already in your library!")
        
        # 💬 Chat section (define selected_papers safely)
        st.markdown("---")
        st.subheader("💬 Chat with your papers")
        
        if st.session_state.user_papers:
            processed_papers = [p for p in st.session_state.user_papers if not p.get('needs_processing')]
            pending_papers = [p for p in st.session_state.user_papers if p.get('needs_processing')]

            if pending_papers:
                st.info(f"⏳ {len(pending_papers)} papers will be processed when you ask questions")

            selected_paper_ids = []  # ✅ always defined
            if processed_papers:
                col1, col2 = st.columns([3, 1])
                with col1:
                    selected_papers = st.multiselect(
                        "Select papers to chat with:",
                        options=[f"{p['title']} ({p['source']})" for p in processed_papers],
                        default=[f"{p['title']} ({p['source']})" for p in processed_papers],
                    )
                with col2:
                    if st.button("🗑️ Clear Chat"):
                        st.session_state.chat_history = []

                for selected in selected_papers:
                    for paper in processed_papers:
                        if f"{paper['title']} ({paper['source']})" == selected:
                            selected_paper_ids.append(paper['paper_id'])
                            break
        else:
            st.warning("⚠️ No papers available. Please upload or fetch from ArXiv first.")
            selected_paper_ids = []
        
        # Display chat history
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if "sources" in message and message["sources"]:
                    st.markdown("**Sources:**")
                    for source in message["sources"]:
                        st.markdown(f"- {source['paper']} (p. {source['page']})")
        
        # Chat input
        if st.session_state.user_papers:  # Allow chat if there are any papers (processed or pending)
            if prompt := st.chat_input("Ask a question about your papers..."):
                # Add user message to chat
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                
                # Display user message
                with st.chat_message("user"):
                    st.markdown(prompt)
                
                # Generate response
                with st.chat_message("assistant"):
                    with st.spinner("Processing papers and thinking..."):
                        try:
                            # Process any papers that need processing
                            papers_to_process = [p for p in st.session_state.user_papers if p.get('needs_processing')]
                            
                            if papers_to_process:
                                st.info(f"📥 Processing {len(papers_to_process)} papers for your query...")
                                
                                for paper in papers_to_process:
                                    try:
                                        # Download and process the paper
                                        pdf_path = arxiv_service.download_paper_pdf(
                                            paper['pdf_url'], 
                                            f"{paper['arxiv_id']}.pdf"
                                        )
                                        
                                        if pdf_path:
                                            # Ingest the PDF
                                            from rag.ingest import PDFIngester
                                            ingester = PDFIngester()
                                            processed_paper_id = ingester.ingest_pdf(pdf_path, st.session_state.user_id)
                                            
                                            # Update paper info
                                            paper['paper_id'] = processed_paper_id
                                            paper['needs_processing'] = False
                                            
                                            # Clean up downloaded file
                                            os.remove(pdf_path)
                                            
                                            st.success(f"✅ Processed: {paper['title']}")
                                        else:
                                            st.error(f"❌ Failed to download: {paper['title']}")
                                            
                                    except Exception as e:
                                        st.error(f"❌ Error processing {paper['title']}: {str(e)}")
                            
                            # Now generate response with processed papers
                            response = rag_chain.generate_response(
                                prompt, 
                                persona, 
                                st.session_state.user_id
                            )
                            
                            # Parse response
                            if isinstance(response, dict):
                                answer = response.get('answer', '')
                                sources = response.get('sources', [])
                            else:
                                answer = response
                                sources = []
                            
                            st.markdown(answer)
                            
                            # Display sources
                            if sources:
                                st.markdown("**Sources:**")
                                for source in sources:
                                    st.markdown(f"- {source['paper']} (p. {source['page']})")
                            
                            # Add assistant message to chat history
                            st.session_state.chat_history.append({
                                "role": "assistant", 
                                "content": answer,
                                "sources": sources
                            })
                            
                            # Save to chat history
                            chat_service.save_message(
                                st.session_state.user_id,
                                prompt,
                                answer,
                                persona,
                                sources
                            )
                            
                        except Exception as e:
                            st.error(f"Error generating response: {str(e)}")
    
    else:
        st.info("Please login to access the chatbot.")
        st.markdown("""
        ### Features:
        - 📄 Upload research paper PDFs
        - 🔍 Search ArXiv for papers by topic
        - 📊 Select number of search results (5-20 papers)
        - 📋 View paper details, authors, and abstracts
        - 📥 Download and process papers automatically
        - 💬 Ask questions about your papers
        - 🎭 Get persona-specific responses (Student/Professor/General)
        - 📚 Source citations with page numbers
        - 🔐 Secure user authentication
        """)

if __name__ == "__main__":
    main()
