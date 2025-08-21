"""
Alternative PDF processing module using pdfplumber and PyPDF2
Use this if PyMuPDF installation fails on Windows
"""

import os
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    try:
        import pdfplumber
        import PyPDF2
        ALTERNATIVE_AVAILABLE = True
    except ImportError:
        ALTERNATIVE_AVAILABLE = False
        print("Warning: No PDF processing libraries available. Install PyMuPDF or pdfplumber+PyPDF2")

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
import weaviate

class AlternativePDFProcessor:
    """Alternative PDF processor using pdfplumber and PyPDF2"""
    
    def __init__(self):
        """Initialize the alternative PDF processor"""
        if not ALTERNATIVE_AVAILABLE:
            raise ImportError("pdfplumber and PyPDF2 are required for alternative PDF processing")
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def extract_text_from_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract text from PDF using pdfplumber"""
        pages = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text and text.strip():
                        pages.append({
                            "page_number": page_num + 1,
                            "text": text.strip()
                        })
        except Exception as e:
            print(f"Error extracting text with pdfplumber: {e}")
            # Fallback to PyPDF2
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page_num, page in enumerate(pdf_reader.pages):
                        text = page.extract_text()
                        if text and text.strip():
                            pages.append({
                                "page_number": page_num + 1,
                                "text": text.strip()
                            })
            except Exception as e2:
                print(f"Error extracting text with PyPDF2: {e2}")
                raise ValueError(f"Could not extract text from PDF: {e2}")
        
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

def get_pdf_processor():
    """Get the appropriate PDF processor based on available libraries"""
    if PYMUPDF_AVAILABLE:
        from rag.ingest import PDFIngester
        return PDFIngester()
    elif ALTERNATIVE_AVAILABLE:
        return AlternativePDFProcessor()
    else:
        raise ImportError(
            "No PDF processing libraries available. "
            "Install PyMuPDF (recommended) or pdfplumber+PyPDF2"
        )

# Example usage:
# processor = get_pdf_processor()
# pages = processor.extract_text_from_pdf("path/to/paper.pdf")
# chunks = processor.chunk_text(pages)
