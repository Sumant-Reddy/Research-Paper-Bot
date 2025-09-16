import fitz  # PyMuPDF
import os
import uuid
from typing import List, Dict, Any
import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import weaviate
from datetime import datetime, timezone
import streamlit as st

class PDFIngester:
    def __init__(self):
        """Initialize the PDF ingester with Google AI embeddings and Weaviate client"""
        # Use Google AI embeddings (Gemini)
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=st.secrets["GOOGLE_API_KEY"],
            task_type="retrieval_document",
            dimension=768
        )
        
        # Initialize Weaviate client with v3 syntax using Streamlit secrets
        weaviate_url = st.secrets["WEAVIATE_URL"]
        weaviate_api_key = st.secrets["WEAVIATE_API_KEY"]
        google_api_key = st.secrets["GOOGLE_API_KEY"]
        
        if not weaviate_url or not weaviate_api_key:
            raise ValueError("Missing Weaviate configuration. Please check WEAVIATE_URL and WEAVIATE_API_KEY in your Streamlit secrets.")
        
        self.client = weaviate.Client(
            url=weaviate_url,
            auth_client_secret=weaviate.AuthApiKey(api_key=weaviate_api_key)
        )
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Ensure schema exists
        self._create_schema()
    
    def _create_schema(self):
        """Create the Weaviate schema for storing paper chunks"""
        # First, try to delete existing schema if it exists
        try:
            self.client.schema.delete_class("PaperChunk")
        except Exception as e:
            print(f"Info: Schema deletion skipped: {e}")
            
        schema = {
            "class": "PaperChunk",
            "description": "A chunk of text from a research paper",
            "vectorIndexConfig": {
                "distance": "cosine",
                "dimension": 768
            },
            "properties": [
                {
                    "name": "content",
                    "dataType": ["text"],
                    "description": "The text content of the chunk"
                },
                {
                    "name": "paper_id",
                    "dataType": ["text"],
                    "description": "Unique identifier for the paper"
                },
                {
                    "name": "paper_title",
                    "dataType": ["text"],
                    "description": "Title of the research paper"
                },
                {
                    "name": "page_number",
                    "dataType": ["int"],
                    "description": "Page number where this chunk appears"
                },
                {
                    "name": "chunk_index",
                    "dataType": ["int"],
                    "description": "Index of this chunk within the paper"
                },
                {
                    "name": "user_id",
                    "dataType": ["text"],
                    "description": "User who uploaded this paper"
                },
                {
                    "name": "upload_date",
                    "dataType": ["date"],
                    "description": "Date when the paper was uploaded"
                }
            ],
            "vectorizer": "none"
        }
        
        try:
            self.client.schema.create_class(schema)
        except Exception as e:
            # Schema might already exist
            pass
    
    def extract_text_from_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract text from PDF with page information"""
        doc = fitz.open(pdf_path)
        pages = []
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            if text.strip():  # Only add non-empty pages
                pages.append({
                    "page_number": page_num + 1,
                    "text": text.strip()
                })
        
        doc.close()
        return pages
    
    def chunk_text(self, pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Split text into chunks while preserving page information"""
        chunks = []
        chunk_index = 0
        
        for page in pages:
            page_text = page["text"]
            page_number = page["page_number"]
            
            # Split the page text into chunks
            page_chunks = self.text_splitter.split_text(page_text)
            
            for chunk_text in page_chunks:
                if chunk_text.strip():  # Only add non-empty chunks
                    chunks.append({
                        "content": chunk_text.strip(),
                        "page_number": page_number,
                        "chunk_index": chunk_index
                    })
                    chunk_index += 1
        
        return chunks
    
    def store_chunks(self, chunks: List[Dict[str, Any]], paper_id: str, 
                    paper_title: str, user_id: str) -> None:
        """Store chunks in Weaviate with manual Gemini embeddings"""
        batch_size = 50  # Smaller batch size for embedding generation
        upload_date = datetime.now(timezone.utc).isoformat()
        
        for i in range(0, len(chunks), batch_size):
            batch_chunks = chunks[i:i + batch_size]
            
            # Insert batch into Weaviate with embeddings
            try:
                self.client.batch.configure(batch_size=batch_size)
                with self.client.batch as batch:
                    for chunk in batch_chunks:
                        # Generate embedding using Gemini
                        embedding = self.embeddings.embed_query(chunk["content"])
                        
                        # Prepare data object
                        data_object = {
                            "content": chunk["content"],
                            "paper_id": paper_id,
                            "paper_title": paper_title,
                            "page_number": chunk["page_number"],
                            "chunk_index": chunk["chunk_index"],
                            "user_id": user_id,
                            "upload_date": upload_date
                        }
                        
                        # Add to batch with vector (since vectorizer is "none")
                        batch.add_data_object(
                            data_object=data_object,
                            class_name="PaperChunk",
                            vector=embedding
                        )
                        
            except Exception as e:
                print(f"Error storing batch: {e}")
                raise
    
    def ingest_pdf(self, pdf_path: str, user_id: str) -> str:
        """Main ingestion pipeline"""
        # Generate unique paper ID
        paper_id = str(uuid.uuid4())
        
        # Extract paper title from filename
        paper_title = os.path.splitext(os.path.basename(pdf_path))[0]
        
        # Extract text from PDF
        pages = self.extract_text_from_pdf(pdf_path)
        
        if not pages:
            raise ValueError("No text content found in PDF")
        
        # Chunk the text
        chunks = self.chunk_text(pages)
        
        if not chunks:
            raise ValueError("No valid chunks created from PDF")
        
        # Store chunks in vector database
        self.store_chunks(chunks, paper_id, paper_title, user_id)
        
        print(f"Ingested {len(chunks)} chunks from {len(pages)} pages")
        return paper_id
    
    def get_paper_info(self, paper_id: str) -> Dict[str, Any]:
        """Get information about a specific paper"""
        query = {
            "class": "PaperChunk",
            "properties": ["paper_title", "user_id", "upload_date"],
            "where": {
                "path": ["paper_id"],
                "operator": "Equal",
                "valueString": paper_id
            },
            "limit": 1
        }
        
        result = self.client.query.get("PaperChunk", ["paper_title", "user_id", "upload_date"]).with_where({
            "path": ["paper_id"],
            "operator": "Equal",
            "valueString": paper_id
        }).with_limit(1).do()
        
        if result["data"]["Get"]["PaperChunk"]:
            return result["data"]["Get"]["PaperChunk"][0]
        return None
