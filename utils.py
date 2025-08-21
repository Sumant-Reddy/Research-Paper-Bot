import re
import hashlib
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
import tiktoken

def clean_text(text: str) -> str:
    """
    Clean and normalize text content
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters that might cause issues
    text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\{\}]', '', text)
    
    # Normalize line breaks
    text = text.replace('\n', ' ').replace('\r', ' ')
    
    return text.strip()

def count_tokens(text: str, model: str = "gpt-4") -> int:
    """
    Count the number of tokens in text
    
    Args:
        text: Text to count tokens for
        model: OpenAI model name
        
    Returns:
        Number of tokens
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except:
        # Fallback: rough estimation (1 token ≈ 4 characters)
        return len(text) // 4

def truncate_text(text: str, max_tokens: int, model: str = "gpt-4") -> str:
    """
    Truncate text to fit within token limit
    
    Args:
        text: Text to truncate
        max_tokens: Maximum number of tokens
        model: OpenAI model name
        
    Returns:
        Truncated text
    """
    if count_tokens(text, model) <= max_tokens:
        return text
    
    # Binary search for the right length
    left, right = 0, len(text)
    while left < right:
        mid = (left + right + 1) // 2
        truncated = text[:mid]
        if count_tokens(truncated, model) <= max_tokens:
            left = mid
        else:
            right = mid - 1
    
    return text[:left]

def extract_paper_metadata(text: str) -> Dict[str, Any]:
    """
    Extract basic metadata from paper text
    
    Args:
        text: Paper text content
        
    Returns:
        Dictionary with extracted metadata
    """
    metadata = {
        "title": "",
        "authors": [],
        "abstract": "",
        "keywords": []
    }
    
    lines = text.split('\n')
    
    # Try to extract title (usually first few lines)
    for i, line in enumerate(lines[:10]):
        line = line.strip()
        if line and len(line) > 10 and len(line) < 200:
            # Check if it looks like a title
            if not line.islower() and not line.isupper():
                metadata["title"] = line
                break
    
    # Try to extract abstract (look for common patterns)
    abstract_start = -1
    for i, line in enumerate(lines):
        line_lower = line.lower().strip()
        if any(keyword in line_lower for keyword in ['abstract', 'summary', 'overview']):
            abstract_start = i + 1
            break
    
    if abstract_start != -1:
        abstract_lines = []
        for line in lines[abstract_start:]:
            line = line.strip()
            if line and not line.startswith('Keywords:') and not line.startswith('1.'):
                abstract_lines.append(line)
            elif line.startswith('Keywords:'):
                break
        metadata["abstract"] = ' '.join(abstract_lines)
    
    return metadata

def generate_paper_id(filename: str, content_hash: str = None) -> str:
    """
    Generate a unique paper ID
    
    Args:
        filename: Original filename
        content_hash: Optional content hash
        
    Returns:
        Unique paper ID
    """
    if content_hash:
        return f"{content_hash}_{uuid.uuid4().hex[:8]}"
    else:
        # Use filename and timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = re.sub(r'[^\w\-_\.]', '_', filename)
        return f"{safe_filename}_{timestamp}_{uuid.uuid4().hex[:8]}"

def validate_email(email: str) -> bool:
    """
    Validate email format
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password: str) -> Dict[str, Any]:
    """
    Validate password strength
    
    Args:
        password: Password to validate
        
    Returns:
        Dictionary with validation results
    """
    result = {
        "valid": True,
        "errors": [],
        "strength": "weak"
    }
    
    if len(password) < 8:
        result["valid"] = False
        result["errors"].append("Password must be at least 8 characters long")
    
    if not re.search(r'[A-Z]', password):
        result["errors"].append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        result["errors"].append("Password must contain at least one lowercase letter")
    
    if not re.search(r'\d', password):
        result["errors"].append("Password must contain at least one number")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        result["errors"].append("Password must contain at least one special character")
    
    if result["errors"]:
        result["valid"] = False
    
    # Determine strength
    if len(password) >= 12 and len(result["errors"]) <= 1:
        result["strength"] = "strong"
    elif len(password) >= 10 and len(result["errors"]) <= 2:
        result["strength"] = "medium"
    else:
        result["strength"] = "weak"
    
    return result

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe storage
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove or replace unsafe characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')
    
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:255-len(ext)-1] + '.' + ext if ext else name[:255]
    
    return filename

def chunk_text_by_sentences(text: str, max_chunk_size: int = 1000) -> List[str]:
    """
    Split text into chunks by sentences while respecting size limits
    
    Args:
        text: Text to chunk
        max_chunk_size: Maximum chunk size in characters
        
    Returns:
        List of text chunks
    """
    # Split by sentences (simple approach)
    sentences = re.split(r'[.!?]+', text)
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        # Add period back
        sentence += "."
        
        # Check if adding this sentence would exceed the limit
        if len(current_chunk) + len(sentence) <= max_chunk_size:
            current_chunk += sentence + " "
        else:
            # Save current chunk and start new one
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + " "
    
    # Add the last chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def extract_citations_from_text(text: str) -> List[Dict[str, Any]]:
    """
    Extract citation information from text
    
    Args:
        text: Text containing citations
        
    Returns:
        List of citation dictionaries
    """
    citations = []
    
    # Look for common citation patterns
    patterns = [
        r'\(([^)]+)\)',  # (Author, Year)
        r'\[([^\]]+)\]',  # [Author, Year]
        r'([A-Z][a-z]+ et al\.?,?\s+\d{4})',  # Author et al., Year
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            citation_text = match.group(1) if len(match.groups()) > 0 else match.group(0)
            citations.append({
                "text": citation_text,
                "start": match.start(),
                "end": match.end(),
                "pattern": pattern
            })
    
    return citations

def calculate_similarity_score(text1: str, text2: str) -> float:
    """
    Calculate simple similarity score between two texts
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        Similarity score (0-1)
    """
    # Simple Jaccard similarity
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union)

def format_timestamp(timestamp: datetime) -> str:
    """
    Format timestamp for display
    
    Args:
        timestamp: Datetime object
        
    Returns:
        Formatted timestamp string
    """
    now = datetime.now()
    diff = now - timestamp
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "Just now"
