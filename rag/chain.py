import os
from typing import List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
import json
import streamlit as st

class RAGChain:
    def __init__(self, retriever):
        """Initialize the RAG chain with retriever and LLM"""
        self.retriever = retriever
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.1,
            google_api_key=st.secrets["GOOGLE_API_KEY"],
            convert_system_message_to_human=True
        )
        
        # Persona-specific prompt templates
        self.persona_prompts = {
            "Student": """You are a helpful AI assistant explaining research papers to students. 
            Your responses should be:
            - Clear and easy to understand
            - Focus on key concepts and takeaways
            - Avoid overly technical jargon
            - Provide practical insights and applications
            - Use analogies when helpful
            
            Always cite your sources with paper title and page number.""",
            
            "Professor": """You are an AI assistant helping professors analyze research papers. 
            Your responses should be:
            - Critical and analytical
            - Identify research gaps and limitations
            - Discuss methodological strengths and weaknesses
            - Compare with related work when relevant
            - Suggest future research directions
            - Use academic language and terminology
            
            Always cite your sources with paper title and page number.""",
            
            "General User": """You are a helpful AI assistant explaining research papers to general users. 
            Your responses should be:
            - Written in plain English
            - Focus on real-world implications
            - Avoid technical jargon
            - Be engaging and accessible
            - Highlight why the research matters
            
            Always cite your sources with paper title and page number."""
        }
    
    def _format_context(self, chunks: List[Dict[str, Any]]) -> str:
        """Format retrieved chunks into context string"""
        if not chunks:
            return "No relevant information found in the uploaded papers."
        
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(f"""
Source {i}: {chunk['paper_title']} (Page {chunk['page_number']})
Content: {chunk['content']}
---""")
        
        return "\n".join(context_parts)
    
    def _extract_sources(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract source information from chunks"""
        sources = []
        seen_sources = set()
        
        for chunk in chunks:
            source_key = f"{chunk['paper_title']}_{chunk['page_number']}"
            if source_key not in seen_sources:
                sources.append({
                    "paper": chunk['paper_title'],
                    "page": chunk['page_number']
                })
                seen_sources.add(source_key)
        
        return sources
    
    def generate_response(self, query: str, persona: str, user_id: str) -> Dict[str, Any]:
        """
        Generate a response using RAG with persona-specific prompting
        
        Args:
            query: User's question
            persona: Target persona (Student/Professor/General User)
            user_id: User ID for filtering papers
            
        Returns:
            Dictionary with answer and sources
        """
        try:
            # Retrieve relevant chunks
            chunks = self.retriever.retrieve_relevant_chunks(query, user_id, top_k=5)
            
            if not chunks:
                return {
                    "answer": "I couldn't find any relevant information in your uploaded papers. Please make sure you have uploaded the papers you'd like me to analyze.",
                    "sources": []
                }
            
            # Format context
            context = self._format_context(chunks)
            
            # Get persona-specific prompt
            persona_prompt = self.persona_prompts.get(persona, self.persona_prompts["General User"])
            
            # Create the full prompt
            system_prompt = f"""{persona_prompt}

You have access to the following information from research papers:

{context}

Based on this information, answer the user's question. Be thorough but concise. Always cite your sources by mentioning the paper title and page number in your response.

Question: {query}"""
            
            # Generate response
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=query)
            ]
            
            response = self.llm.invoke(messages)
            answer = response.content
            
            # Extract sources
            sources = self._extract_sources(chunks)
            
            return {
                "answer": answer,
                "sources": sources
            }
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return {
                "answer": f"I encountered an error while processing your question: {str(e)}. Please try again.",
                "sources": []
            }
    
    def generate_summary(self, paper_id: str, user_id: str, persona: str) -> Dict[str, Any]:
        """
        Generate a summary of a specific paper
        
        Args:
            paper_id: The paper to summarize
            user_id: User ID for verification
            persona: Target persona for summary style
            
        Returns:
            Dictionary with summary and sources
        """
        try:
            # Retrieve chunks from the specific paper
            chunks = self.retriever.retrieve_by_paper_id(paper_id, user_id, top_k=20)
            
            if not chunks:
                return {
                    "answer": "I couldn't find the specified paper in your uploaded documents.",
                    "sources": []
                }
            
            # Format context
            context = self._format_context(chunks)
            
            # Get persona-specific prompt for summarization
            persona_prompt = self.persona_prompts.get(persona, self.persona_prompts["General User"])
            
            # Create summarization prompt
            system_prompt = f"""{persona_prompt}

You have access to the following information from a research paper:

{context}

Please provide a comprehensive summary of this paper. Include:
1. Main research question/problem
2. Methodology used
3. Key findings
4. Implications and conclusions

Write the summary in a way that's appropriate for the {persona} persona.

Paper: {chunks[0]['paper_title']}"""
            
            # Generate summary
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content="Please summarize this research paper.")
            ]
            
            response = self.llm.invoke(messages)
            summary = response.content
            
            # Extract sources
            sources = self._extract_sources(chunks)
            
            return {
                "answer": summary,
                "sources": sources
            }
            
        except Exception as e:
            print(f"Error generating summary: {e}")
            return {
                "answer": f"I encountered an error while summarizing the paper: {str(e)}. Please try again.",
                "sources": []
            }
    
    def generate_comparison(self, query: str, user_id: str, persona: str) -> Dict[str, Any]:
        """
        Generate a comparison response across multiple papers
        
        Args:
            query: User's question about comparing papers
            user_id: User ID for filtering papers
            persona: Target persona for response style
            
        Returns:
            Dictionary with comparison and sources
        """
        try:
            # Retrieve relevant chunks from multiple papers
            chunks = self.retriever.retrieve_relevant_chunks(query, user_id, top_k=10)
            
            if not chunks:
                return {
                    "answer": "I couldn't find any relevant information in your uploaded papers for comparison.",
                    "sources": []
                }
            
            # Format context
            context = self._format_context(chunks)
            
            # Get persona-specific prompt
            persona_prompt = self.persona_prompts.get(persona, self.persona_prompts["General User"])
            
            # Create comparison prompt
            system_prompt = f"""{persona_prompt}

You have access to information from multiple research papers:

{context}

The user is asking for a comparison or analysis across these papers. Please provide a thoughtful comparison that:
1. Identifies common themes and differences
2. Highlights strengths and weaknesses of different approaches
3. Provides insights that are appropriate for the {persona} persona

Question: {query}"""
            
            # Generate comparison
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=query)
            ]
            
            response = self.llm.invoke(messages)
            comparison = response.content
            
            # Extract sources
            sources = self._extract_sources(chunks)
            
            return {
                "answer": comparison,
                "sources": sources
            }
            
        except Exception as e:
            print(f"Error generating comparison: {e}")
            return {
                "answer": f"I encountered an error while generating the comparison: {str(e)}. Please try again.",
                "sources": []
            }
