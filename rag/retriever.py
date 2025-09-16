import os
import weaviate
from typing import List, Dict, Any
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import streamlit as st

class RAGRetriever:
    def __init__(self):
        """Initialize the RAG retriever with Weaviate client and Google AI embeddings"""
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
    
    def retrieve_relevant_chunks(self, query: str, user_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve the most relevant chunks for a given query
        
        Args:
            query: The user's question
            user_id: The user's ID to filter papers
            top_k: Number of chunks to retrieve
            
        Returns:
            List of relevant chunks with metadata
        """
        try:
            # Get query embedding
            query_embedding = self.embeddings.embed_query(query)
            
            # Search in Weaviate
            result = (
                self.client.query
                .get("PaperChunk", [
                    "content", 
                    "paper_id", 
                    "paper_title", 
                    "page_number", 
                    "chunk_index",
                    "user_id"
                ])
                .with_near_vector({
                    "vector": query_embedding
                })
                .with_where({
                    "path": ["user_id"],
                    "operator": "Equal",
                    "valueString": user_id
                })
                .with_limit(top_k)
                .with_additional(["distance"])
                .do()
            )
            
            # Process results
            chunks = []
            if result["data"]["Get"]["PaperChunk"]:
                for item in result["data"]["Get"]["PaperChunk"]:
                    chunks.append({
                        "content": item["content"],
                        "paper_id": item["paper_id"],
                        "paper_title": item["paper_title"],
                        "page_number": item["page_number"],
                        "chunk_index": item["chunk_index"],
                        "distance": item["_additional"]["distance"],
                        "user_id": item["user_id"]
                    })
            
            return chunks
            
        except Exception as e:
            print(f"Error retrieving chunks: {e}")
            return []
    
    def retrieve_by_paper_id(self, paper_id: str, user_id: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve chunks from a specific paper
        
        Args:
            paper_id: The paper ID to search in
            user_id: The user's ID for verification
            top_k: Number of chunks to retrieve
            
        Returns:
            List of chunks from the specified paper
        """
        try:
            result = (
                self.client.query
                .get("PaperChunk", [
                    "content", 
                    "paper_id", 
                    "paper_title", 
                    "page_number", 
                    "chunk_index",
                    "user_id"
                ])
                .with_where({
                    "operator": "And",
                    "operands": [
                        {
                            "path": ["paper_id"],
                            "operator": "Equal",
                            "valueString": paper_id
                        },
                        {
                            "path": ["user_id"],
                            "operator": "Equal",
                            "valueString": user_id
                        }
                    ]
                })
                .with_limit(top_k)
                .do()
            )
            
            chunks = []
            if result["data"]["Get"]["PaperChunk"]:
                for item in result["data"]["Get"]["PaperChunk"]:
                    chunks.append({
                        "content": item["content"],
                        "paper_id": item["paper_id"],
                        "paper_title": item["paper_title"],
                        "page_number": item["page_number"],
                        "chunk_index": item["chunk_index"],
                        "user_id": item["user_id"]
                    })
            
            return chunks
            
        except Exception as e:
            print(f"Error retrieving chunks by paper ID: {e}")
            return []
    
    def get_user_papers(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all papers uploaded by a user
        
        Args:
            user_id: The user's ID
            
        Returns:
            List of paper information
        """
        try:
            result = (
                self.client.query
                .get("PaperChunk", [
                    "paper_id", 
                    "paper_title", 
                    "upload_date"
                ])
                .with_where({
                    "path": ["user_id"],
                    "operator": "Equal",
                    "valueString": user_id
                })
                .with_limit(1000)  # Get more chunks to ensure we find all papers
                .do()
            )
            
            papers = []
            if result["data"]["Get"]["PaperChunk"]:
                seen_papers = set()
                for item in result["data"]["Get"]["PaperChunk"]:
                    paper_id = item["paper_id"]
                    if paper_id not in seen_papers:
                        papers.append({
                            "paper_id": paper_id,
                            "paper_title": item["paper_title"],
                            "upload_date": item["upload_date"]
                        })
                        seen_papers.add(paper_id)
            
            return papers
            
        except Exception as e:
            print(f"Error getting user papers: {e}")
            return []
    
    def search_similar_chunks(self, chunk_content: str, user_id: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Find chunks similar to a given chunk content
        
        Args:
            chunk_content: The content to find similar chunks for
            user_id: The user's ID to filter papers
            top_k: Number of similar chunks to retrieve
            
        Returns:
            List of similar chunks
        """
        try:
            # Get embedding for the chunk content
            chunk_embedding = self.embeddings.embed_query(chunk_content)
            
            # Search for similar chunks
            result = (
                self.client.query
                .get("PaperChunk", [
                    "content", 
                    "paper_id", 
                    "paper_title", 
                    "page_number", 
                    "chunk_index",
                    "user_id"
                ])
                .with_near_vector({
                    "vector": chunk_embedding
                })
                .with_where({
                    "path": ["user_id"],
                    "operator": "Equal",
                    "valueString": user_id
                })
                .with_limit(top_k)
                .with_additional(["distance"])
                .do()
            )
            
            chunks = []
            if result["data"]["Get"]["PaperChunk"]:
                for item in result["data"]["Get"]["PaperChunk"]:
                    chunks.append({
                        "content": item["content"],
                        "paper_id": item["paper_id"],
                        "paper_title": item["paper_title"],
                        "page_number": item["page_number"],
                        "chunk_index": item["chunk_index"],
                        "distance": item["_additional"]["distance"],
                        "user_id": item["user_id"]
                    })
            
            return chunks
            
        except Exception as e:
            print(f"Error searching similar chunks: {e}")
            return []
