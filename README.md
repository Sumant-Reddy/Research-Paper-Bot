# 📚 Research Paper Chatbot

A full-stack research paper chatbot using Retrieval-Augmented Generation (RAG) with persona-specific responses. Users can upload PDFs, search ArXiv, and get AI-powered answers grounded in their research papers.

## 🚀 Features

- **📄 PDF Upload & Processing**: Automatic text extraction, chunking, and embedding
- **🔍 ArXiv Integration**: Search and fetch papers by topic with lazy processing
- **🎭 Persona-Specific Responses**: Student, Professor, and General User modes
- **📚 Source Citations**: Every answer includes paper title and page numbers
- **🔐 User Authentication**: Secure login/signup with Firebase
- **💬 Chat Interface**: Interactive conversation with history
- **🌐 Multi-Document Support**: Ask questions across multiple papers
- **☁️ Cloud Ready**: Fully configured for Streamlit Cloud deployment

## 🛠️ Tech Stack

- **Backend**: Python with LangChain + Google Gemini API
- **LLM**: Gemini 1.5 Flash for Q&A, Google AI Embeddings (models/embedding-001)
- **Vector Database**: Weaviate Cloud (free tier)
- **Authentication**: Firebase Authentication
- **Frontend**: Streamlit with modern chatbot UI
- **PDF Processing**: PyMuPDF for text extraction
- **Deployment**: Streamlit Cloud (free)

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- Google AI API Key
- Weaviate Cloud account
- Firebase project (optional)

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/PaperBot-V2.git
   cd PaperBot-V2
   ```

2. **Run the quick start script**:
   ```bash
   python quick_start.py
   ```

3. **Or install manually**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   Create a `.env` file with your API keys:
   ```env
   # Google AI Configuration
   GOOGLE_API_KEY=your_google_api_key_here
   
   # Weaviate Cloud Configuration
   WEAVIATE_URL=your_weaviate_cloud_url_here
   WEAVIATE_API_KEY=your_weaviate_api_key_here
   
   # Firebase Configuration (optional)
   FIREBASE_PROJECT_ID=your_firebase_project_id
   FIREBASE_PRIVATE_KEY_ID=your_firebase_private_key_id
   FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYour private key here\n-----END PRIVATE KEY-----\n"
   FIREBASE_CLIENT_EMAIL=your_firebase_client_email
   FIREBASE_CLIENT_ID=your_firebase_client_id
   FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
   FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
   FIREBASE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
   FIREBASE_CLIENT_X509_CERT_URL=your_firebase_client_x509_cert_url
   
   # App Configuration
   SECRET_KEY=your-secret-key-here
   ```

5. **Run the application**:
   ```bash
   streamlit run app/main.py
   ```

## 🏗️ Project Structure

```
PaperBot-V2/
├── 📁 app/
│   ├── __init__.py
│   └── main.py              # Main Streamlit application
├── 📁 rag/
│   ├── __init__.py
│   ├── ingest.py            # PDF ingestion and chunking
│   ├── retriever.py         # Vector search and retrieval
│   ├── chain.py             # RAG chain and prompts
│   └── pdf_processor_alt.py # Alternative PDF processor
├── 📁 services/
│   ├── __init__.py
│   ├── auth_service.py      # Firebase authentication
│   ├── chat_service.py      # Chat history management
│   └── arxiv_service.py     # ArXiv paper fetching
├── 📁 .streamlit/
│   └── secrets.toml         # Streamlit Cloud secrets (configured)
├── 📄 README.md             # This file
├── 📄 LICENSE               # MIT License
├── 📄 .gitignore            # Git ignore rules
├── 📄 requirements.txt      # Python dependencies
├── 📄 quick_start.py        # Quick start script
├── 📄 utils.py              # Utility functions
└── 📄 PROJECT_SUMMARY.md    # Complete project overview
```

## 🎯 Usage

### 1. Authentication
- Sign up with email/password or use demo credentials
- Firebase authentication for secure user management

### 2. Upload Papers
- **Direct Upload**: Drag and drop PDF files
- **ArXiv Search**: Search for papers by topic and add to library
- **Lazy Processing**: Papers are processed on-demand when you ask questions

### 3. Chat with Papers
- Select papers from your library
- Choose your persona (Student/Professor/General User)
- Ask questions and get grounded responses with citations

### 4. Persona Modes
- **Student**: Simplified explanations with key takeaways
- **Professor**: Critical analysis with research gaps and methodology
- **General User**: Plain English explanations with real-world implications

## 🚀 Deployment

### Streamlit Cloud Deployment

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Research Paper Chatbot v2.0.0"
   git remote add origin https://github.com/YOUR_USERNAME/PaperBot-V2.git
   git branch -M main
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository: `YOUR_USERNAME/PaperBot-V2`
   - Set main file path: `app/main.py`
   - Click "Deploy"

3. **Configure Secrets**:
   - In your deployed app, go to Settings → Secrets
   - Add your API keys in TOML format (see `.streamlit/secrets.toml`)

Your app will be live at: `https://your-app-name.streamlit.app`

## 🔧 Configuration

### API Keys Required

1. **Google AI API Key**:
   - Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Used for Gemini LLM and embeddings

2. **Weaviate Cloud**:
   - Sign up at [Weaviate Cloud](https://console.weaviate.cloud/)
   - Get URL and API key from your cluster

3. **Firebase (Optional)**:
   - Create project at [Firebase Console](https://console.firebase.google.com/)
   - Download service account key
   - Enable Authentication

### Environment Variables

All configuration is handled through Streamlit secrets for deployment:

```toml
# Google AI Configuration
GOOGLE_API_KEY = "your_google_api_key"

# Weaviate Cloud Configuration
WEAVIATE_URL = "your_weaviate_cloud_url"
WEAVIATE_API_KEY = "your_weaviate_api_key"

# Firebase Configuration
FIREBASE_PROJECT_ID = "your_firebase_project_id"
FIREBASE_PRIVATE_KEY_ID = "your_firebase_private_key_id"
FIREBASE_PRIVATE_KEY = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL = "your_firebase_client_email"
FIREBASE_CLIENT_ID = "your_firebase_client_id"
FIREBASE_AUTH_URI = "https://accounts.google.com/o/oauth2/auth"
FIREBASE_TOKEN_URI = "https://oauth2.googleapis.com/token"
FIREBASE_AUTH_PROVIDER_X509_CERT_URL = "https://www.googleapis.com/oauth2/v1/certs"
FIREBASE_CLIENT_X509_CERT_URL = "your_firebase_client_x509_cert_url"

# App Configuration
SECRET_KEY = "your-secret-key-here"
```

## 🧪 Testing

### Local Testing

1. **Test imports**:
   ```bash
   python -c "import streamlit, langchain, weaviate, fitz, firebase_admin, arxiv; print('All imports successful!')"
   ```

2. **Test services**:
   ```bash
   python quick_start.py
   ```

3. **Run the app**:
   ```bash
   streamlit run app/main.py
   ```

### Deployment Testing

1. **Check Streamlit Cloud logs** for any errors
2. **Verify API connections** in the app
3. **Test all features**: upload, search, chat, authentication

## 🔍 Troubleshooting

### Common Issues

1. **Import Errors**:
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version (3.8+ required)

2. **API Key Errors**:
   - Verify all API keys are correctly set in Streamlit secrets
   - Check that keys have proper permissions

3. **Weaviate Connection Issues**:
   - Verify Weaviate URL and API key
   - Check if your Weaviate cluster is running

4. **Firebase Authentication Issues**:
   - Verify Firebase project configuration
   - Check service account credentials

### Debug Mode

To enable debug mode, add to your secrets:
```toml
DEBUG = "true"
```

## 📊 Performance

- **Response Time**: ~2-5 seconds for typical queries
- **Memory Usage**: Optimized for Streamlit Cloud limits
- **Cost**: Uses free tiers where possible
- **Scalability**: Supports multiple users and papers

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LangChain**: RAG framework
- **Google Gemini**: LLM and embeddings
- **Weaviate**: Vector database
- **Streamlit**: Web framework
- **Firebase**: Authentication
- **PyMuPDF**: PDF processing

## 📞 Support

- **Documentation**: Check [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) for detailed overview
- **Issues**: Create an issue on GitHub
- **Discussions**: Use GitHub Discussions for questions

---

**🎉 Ready to deploy!** Your Research Paper Chatbot is fully configured for Streamlit Cloud deployment with all API keys and services integrated.
