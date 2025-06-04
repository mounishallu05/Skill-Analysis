import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import re
from pathlib import Path

logger = logging.getLogger(__name__)

def setup_logging(log_file: str = 'logs/app.log', level: str = 'INFO'):
    """
    Set up logging configuration
    
    Args:
        log_file (str): Path to log file
        level (str): Logging level
    """
    # Create logs directory if it doesn't exist
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def clean_text(text: str) -> str:
    """
    Clean text by removing special characters and extra whitespace
    
    Args:
        text (str): Text to clean
        
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Remove special characters and extra whitespace
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def parse_date(date_str: str) -> Optional[datetime]:
    """
    Parse date string into datetime object
    
    Args:
        date_str (str): Date string to parse
        
    Returns:
        Optional[datetime]: Parsed datetime object or None if parsing fails
    """
    if not date_str:
        return None
        
    try:
        # Try common date formats
        formats = [
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%d/%m/%Y',
            '%B %Y',
            '%b %Y',
            '%Y'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
                
        return None
    except Exception as e:
        logger.error(f"Error parsing date {date_str}: {str(e)}")
        return None

def save_json(data: Dict[str, Any], filepath: str):
    """
    Save data to JSON file
    
    Args:
        data (Dict[str, Any]): Data to save
        filepath (str): Path to save file
    """
    try:
        # Create directory if it doesn't exist
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Data saved to {filepath}")
    except Exception as e:
        logger.error(f"Error saving data to {filepath}: {str(e)}")
        raise

def load_json(filepath: str) -> Dict[str, Any]:
    """
    Load data from JSON file
    
    Args:
        filepath (str): Path to JSON file
        
    Returns:
        Dict[str, Any]: Loaded data
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading data from {filepath}: {str(e)}")
        raise

def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split list into chunks of specified size
    
    Args:
        lst (List[Any]): List to split
        chunk_size (int): Size of each chunk
        
    Returns:
        List[List[Any]]: List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def safe_get(obj: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    """
    Safely get nested dictionary values
    
    Args:
        obj (Dict[str, Any]): Dictionary to get value from
        *keys (str): Keys to traverse
        default (Any): Default value if key not found
        
    Returns:
        Any: Value at specified path or default value
    """
    current = obj
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key, default)
        else:
            return default
    return current 