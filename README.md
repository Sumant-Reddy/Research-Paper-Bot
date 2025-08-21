# 📚 Research Paper Chatbot

A full-stack research paper chatbot using Retrieval-Augmented Generation (RAG) with persona-specific responses. Upload PDFs, ask questions, and get AI-powered answers grounded in your research papers.

## ✨ Features

- **📄 PDF Upload & Processing**: Upload research paper PDFs and automatically extract, chunk, and embed content
- **🔍 ArXiv Integration**: Search and fetch papers directly from ArXiv by topic
- **🎭 Persona-Specific Responses**: Get tailored answers for:
  - **Student**: Clear explanations with key takeaways
  - **Professor**: Critical analysis with academic depth
  - **General User**: Plain English explanations
- **📚 Source Citations**: Every answer includes paper title and page number citations
- **🔐 User Authentication**: Secure login/signup with Firebase Auth
- **💬 Chat Interface**: Interactive Streamlit chatbot with conversation history
- **🌐 Multi-Document Support**: Ask questions across multiple uploaded papers
- **☁️ Cloud Deployment**: Ready for Streamlit Cloud deployment

## 🛠️ Tech Stack

- **Backend**: Python with LangChain + Google Gemini API
- **LLM**: Gemini 1.5 Flash for Q&A, Google AI Embeddings (models/embedding-001)
- **Vector Database**: Weaviate Cloud (free tier)
- **Authentication**: Firebase Authentication
- **Frontend**: Streamlit with modern chatbot UI
- **PDF Processing**: PyMuPDF for text extraction
- **Deployment**: Streamlit Cloud (free)

## 🚀 Quick Start

### Prerequisites

- Python 3.8+ (3.12 recommended for best compatibility)
- Google AI API key
- Weaviate Cloud account (free tier)
- Firebase project (optional, for authentication)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd PaperBot-V2
```

### 2. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt
```

**Note**: If you encounter PyMuPDF installation issues on Windows, try:
```bash
pip install PyMuPDF==1.26.3 --only-binary=PyMuPDF
```

### 3. Set Up Environment Variables

Create a `.env` file in the root directory:

```env
# Google AI Configuration
GOOGLE_API_KEY=your_google_api_key_here

# Weaviate Cloud Configuration
WEAVIATE_URL=your_weaviate_cloud_url_here
WEAVIATE_API_KEY=your_weaviate_api_key_here

# Firebase Configuration (optional for demo)
FIREBASE_PROJECT_ID=your_firebase_project_id
FIREBASE_PRIVATE_KEY_ID=your_firebase_private_key_id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYour private key here\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=your_firebase_client_email
FIREBASE_CLIENT_ID=your_firebase_client_id
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
FIREBASE_CLIENT_X509_CERT_URL=your_firebase_client_x509_cert_url
```

### 4. Run the Application

```bash
# Start the Streamlit app
streamlit run app/main.py
```

The application will be available at `http://localhost:8501`

## 📁 Project Structure

```
PaperBot-V2/
├── app/
│   ├── __init__.py
│   └── main.py              # Main Streamlit application
├── rag/
│   ├── __init__.py
│   ├── ingest.py            # PDF ingestion and chunking
│   ├── retriever.py         # Vector search and retrieval
│   ├── chain.py             # RAG chain and prompts
│   └── pdf_processor_alt.py # Alternative PDF processor
├── services/
│   ├── __init__.py
│   ├── auth_service.py      # Firebase authentication
│   ├── chat_service.py      # Chat history management
│   └── arxiv_service.py     # ArXiv paper fetching
├── utils.py                 # Utility functions
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── .env                    # Environment variables (create this)
```

## 🔧 Configuration

### Google AI API Setup

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file as `GOOGLE_API_KEY`

### Weaviate Cloud Setup

1. Sign up at [Weaviate Cloud](https://console.weaviate.cloud/)
2. Create a new cluster (free tier available)
3. Get your cluster URL and API key
4. Add them to your `.env` file

### Firebase Setup (Optional)

1. Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
2. Enable Authentication (Email/Password)
3. Create a service account and download the credentials
4. Add Firebase credentials to your `.env` file

## 🎯 Usage

### 1. Authentication

- Sign up with email/password or use the demo mode
- Each user has their own paper library and chat history

### 2. Adding Papers

**Option A: Upload PDF**
- Click "Upload PDF" and select your research paper
- The system will automatically process and chunk the document

**Option B: Search ArXiv**
- Enter a topic (e.g., "machine learning")
- Select number of results (5-20)
- Browse papers and add them to your library
- Papers are processed on-demand when you ask questions

### 3. Chatting with Papers

- Select papers from your library
- Choose your persona (Student/Professor/General User)
- Ask questions about the papers
- Get AI-powered responses with source citations

## 🚀 Deployment

### Streamlit Cloud Deployment

1. Push your code to GitHub
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect your GitHub repository
4. Set environment variables in Streamlit Cloud settings
5. Deploy!

### Environment Variables for Deployment

Set these in your deployment platform:

```env
GOOGLE_API_KEY=your_google_api_key
WEAVIATE_URL=your_weaviate_url
WEAVIATE_API_KEY=your_weaviate_api_key
FIREBASE_PROJECT_ID=your_firebase_project_id
FIREBASE_PRIVATE_KEY_ID=your_firebase_private_key_id
FIREBASE_PRIVATE_KEY=your_firebase_private_key
FIREBASE_CLIENT_EMAIL=your_firebase_client_email
FIREBASE_CLIENT_ID=your_firebase_client_id
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
FIREBASE_CLIENT_X509_CERT_URL=your_firebase_client_x509_cert_url
```

## 🔍 Testing

Run the test scripts to verify your setup:

```bash
# Test basic functionality
python test_weaviate_usage.py

# Test ArXiv integration
python test_arxiv_integration.py

# Test file management
python test_file_management.py
```

## 🛠️ Development

### Adding New Features

1. **New RAG Components**: Add to `rag/` directory
2. **New Services**: Add to `services/` directory
3. **UI Changes**: Modify `app/main.py`

### Code Style

- Follow PEP 8 guidelines
- Add docstrings to functions and classes
- Use type hints where appropriate

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [LangChain](https://langchain.com/) for the RAG framework
- [Google AI](https://ai.google/) for the Gemini models
- [Weaviate](https://weaviate.io/) for the vector database
- [Streamlit](https://streamlit.io/) for the web interface
- [Firebase](https://firebase.google.com/) for authentication

## 📞 Support

If you encounter any issues:

1. Check the [Issues](https://github.com/yourusername/PaperBot-V2/issues) page
2. Create a new issue with detailed information
3. Include error messages and steps to reproduce

## 🔄 Changelog

### Version 2.0.0
- Migrated from OpenAI to Google Gemini
- Added ArXiv integration with lazy processing
- Improved file management and state handling
- Optimized page reloads and performance
- Enhanced error handling and user feedback

### Version 1.0.0
- Initial release with OpenAI integration
- Basic RAG functionality
- Streamlit interface
- Firebase authentication
