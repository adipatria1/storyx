from pytube import YouTube
import re
from urllib.parse import urlparse, parse_qs

def is_valid_youtube_url(url: str) -> bool:
    """Validate if the URL is a valid YouTube video URL."""
    try:
        # Parse the URL
        parsed_url = urlparse(url)
        
        # Check if domain is youtube.com or youtu.be
        if not ('youtube.com' in parsed_url.netloc or 'youtu.be' in parsed_url.netloc):
            return False
            
        # Get video ID
        video_id = extract_video_id(url)
        if not video_id:
            return False
            
        # Try to initialize YouTube object to verify video exists
        yt = YouTube(url)
        # Access title to verify video is accessible
        _ = yt.title
        return True
        
    except Exception:
        return False

def extract_video_id(url: str) -> str:
    """Extract YouTube video ID from URL."""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?]*)',
        r'(?:youtube\.com\/embed\/)([^&\n?]*)',
        r'(?:youtube\.com\/v\/)([^&\n?]*)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_video_content(url: str) -> str:
    """Get video content from YouTube URL."""
    if not is_valid_youtube_url(url):
        return "Error: Invalid or inaccessible YouTube URL"
        
    try:
        yt = YouTube(url)
        content = []
        
        # Get title and description
        content.append(f"Title: {yt.title}")
        content.append(f"Description: {yt.description}")
        
        # Get captions if available
        try:
            captions = yt.captions.get_by_language_code('en')
            if captions:
                content.append(captions.generate_srt_captions())
        except:
            pass
            
        return "\n".join(content)
    except Exception as e:
        return f"Error getting video content: {str(e)}"