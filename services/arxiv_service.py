import arxiv
import os
import requests
import tempfile
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
import fitz  # PyMuPDF

class ArXivService:
    def __init__(self):
        """Initialize ArXiv service for fetching research papers"""
        self.base_url = "http://export.arxiv.org/api/query"
    
    def search_papers(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for papers on ArXiv by topic
        
        Args:
            query: Search query (e.g., "machine learning", "quantum computing")
            max_results: Maximum number of results to return
            
        Returns:
            List of paper information
        """
        try:
            # Search ArXiv
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.Relevance
            )
            
            papers = []
            for result in search.results():
                # Extract clean ArXiv ID from entry_id
                arxiv_id = result.entry_id.split('/')[-1]
                
                paper_info = {
                    "id": arxiv_id,
                    "title": result.title,
                    "authors": [author.name for author in result.authors],
                    "summary": result.summary,
                    "published": result.published.strftime("%Y-%m-%d"),
                    "updated": result.updated.strftime("%Y-%m-%d"),
                    "categories": result.categories,
                    "pdf_url": result.pdf_url,
                    "doi": result.doi if hasattr(result, 'doi') else None
                }
                papers.append(paper_info)
            
            return papers
            
        except Exception as e:
            print(f"Error searching ArXiv: {e}")
            return []
    
    def get_paper_by_id(self, paper_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific paper by its ArXiv ID
        
        Args:
            paper_id: ArXiv paper ID (e.g., "2103.12345")
            
        Returns:
            Paper information or None if not found
        """
        try:
            search = arxiv.Search(id_list=[paper_id])
            results = list(search.results())
            
            if results:
                result = results[0]
                # Extract clean ArXiv ID from entry_id
                arxiv_id = result.entry_id.split('/')[-1]
                
                paper_info = {
                    "id": arxiv_id,
                    "title": result.title,
                    "authors": [author.name for author in result.authors],
                    "summary": result.summary,
                    "published": result.published.strftime("%Y-%m-%d"),
                    "updated": result.updated.strftime("%Y-%m-%d"),
                    "categories": result.categories,
                    "pdf_url": result.pdf_url,
                    "doi": result.doi if hasattr(result, 'doi') else None
                }
                return paper_info
            
            return None
            
        except Exception as e:
            print(f"Error getting paper by ID: {e}")
            return None
    
    def download_paper_pdf(self, pdf_url: str, filename: str = None) -> Optional[str]:
        """
        Download a paper PDF from ArXiv
        
        Args:
            pdf_url: URL of the PDF
            filename: Optional filename for the downloaded file
            
        Returns:
            Path to downloaded PDF file or None if failed
        """
        try:
            # Download the PDF
            response = requests.get(pdf_url, stream=True)
            response.raise_for_status()
            
            # Generate filename if not provided
            if not filename:
                # Extract filename from URL
                parsed_url = urlparse(pdf_url)
                filename = os.path.basename(parsed_url.path)
                if not filename.endswith('.pdf'):
                    filename += '.pdf'
            
            # Create a dedicated directory for ArXiv papers
            arxiv_dir = os.path.join(tempfile.gettempdir(), "arxiv_papers")
            os.makedirs(arxiv_dir, exist_ok=True)
            
            # Create unique filename to avoid conflicts
            if not filename.startswith("arxiv_"):
                filename = f"arxiv_{filename}"
            
            file_path = os.path.join(arxiv_dir, filename)
            
            # Save the PDF
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return file_path
            
        except Exception as e:
            print(f"Error downloading PDF: {e}")
            return None
    
    def search_and_download(self, query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """
        Search for papers and download their PDFs
        
        Args:
            query: Search query
            max_results: Maximum number of papers to download
            
        Returns:
            List of papers with local PDF paths
        """
        try:
            # Search for papers
            papers = self.search_papers(query, max_results)
            
            # Download PDFs
            for paper in papers:
                pdf_path = self.download_paper_pdf(paper['pdf_url'], f"{paper['id']}.pdf")
                paper['local_pdf_path'] = pdf_path
            
            return papers
            
        except Exception as e:
            print(f"Error in search and download: {e}")
            return []
    
    def get_paper_metadata(self, paper_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a paper without downloading the PDF
        
        Args:
            paper_id: ArXiv paper ID
            
        Returns:
            Paper metadata or None if not found
        """
        try:
            # Construct the API URL
            api_url = f"{self.base_url}?id_list={paper_id}"
            
            # Make the request
            response = requests.get(api_url)
            response.raise_for_status()
            
            # Parse the XML response (simplified)
            # In a full implementation, you'd use XML parsing
            content = response.text
            
            # Extract basic information (simplified parsing)
            paper_info = {
                "id": paper_id,
                "title": self._extract_title(content),
                "authors": self._extract_authors(content),
                "summary": self._extract_summary(content),
                "pdf_url": f"https://arxiv.org/pdf/{paper_id}.pdf"
            }
            
            return paper_info
            
        except Exception as e:
            print(f"Error getting paper metadata: {e}")
            return None
    
    def _extract_title(self, xml_content: str) -> str:
        """Extract title from ArXiv XML response"""
        try:
            start_tag = "<title>"
            end_tag = "</title>"
            start_idx = xml_content.find(start_tag) + len(start_tag)
            end_idx = xml_content.find(end_tag, start_idx)
            return xml_content[start_idx:end_idx].strip()
        except:
            return "Unknown Title"
    
    def _extract_authors(self, xml_content: str) -> List[str]:
        """Extract authors from ArXiv XML response"""
        try:
            authors = []
            start_tag = "<name>"
            end_tag = "</name>"
            start_idx = 0
            
            while True:
                start_idx = xml_content.find(start_tag, start_idx)
                if start_idx == -1:
                    break
                start_idx += len(start_tag)
                end_idx = xml_content.find(end_tag, start_idx)
                author = xml_content[start_idx:end_idx].strip()
                authors.append(author)
            
            return authors
        except:
            return ["Unknown Author"]
    
    def _extract_summary(self, xml_content: str) -> str:
        """Extract summary from ArXiv XML response"""
        try:
            start_tag = "<summary>"
            end_tag = "</summary>"
            start_idx = xml_content.find(start_tag) + len(start_tag)
            end_idx = xml_content.find(end_tag, start_idx)
            return xml_content[start_idx:end_idx].strip()
        except:
            return "No summary available"
    
    def get_recent_papers(self, category: str = "cs.AI", max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent papers from a specific category
        
        Args:
            category: ArXiv category (e.g., "cs.AI", "cs.LG", "quant-ph")
            max_results: Maximum number of results
            
        Returns:
            List of recent papers
        """
        try:
            # Search for recent papers in the category
            query = f"cat:{category}"
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate
            )
            
            papers = []
            for result in search.results():
                paper_info = {
                    "id": result.entry_id,
                    "title": result.title,
                    "authors": [author.name for author in result.authors],
                    "summary": result.summary,
                    "published": result.published.strftime("%Y-%m-%d"),
                    "updated": result.updated.strftime("%Y-%m-%d"),
                    "categories": result.categories,
                    "pdf_url": result.pdf_url,
                    "doi": result.doi if hasattr(result, 'doi') else None
                }
                papers.append(paper_info)
            
            return papers
            
        except Exception as e:
            print(f"Error getting recent papers: {e}")
            return []
    
    def validate_paper_id(self, paper_id: str) -> bool:
        """
        Validate if a paper ID is in correct ArXiv format
        
        Args:
            paper_id: Paper ID to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # ArXiv IDs typically follow pattern: YYMM.NNNNN
            # or full URL format
            if paper_id.startswith("http"):
                # Extract ID from URL
                paper_id = paper_id.split("/")[-1]
            
            # Check if it matches the pattern
            parts = paper_id.split(".")
            if len(parts) != 2:
                return False
            
            year_month, number = parts
            if len(year_month) != 4 or not year_month.isdigit():
                return False
            
            if not number.isdigit():
                return False
            
            return True
            
        except:
            return False
