import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

AVAILABLE_MODELS = [
    'gemini-1.0-pro',
    'gemini-1.5-flash',
    'gemini-1.5-flash-8b',
    'gemini-1.5-flash-8b-exp',
    'gemini-1.5-flash-exp',
    'gemini-1.5-pro',
    'gemini-1.5-pro-exp',
    'gemini-2.0-flash-exp'
]

EXPERTISE_LEVELS = [
    'storyteller',
    'novelist',
    'journalist',
    'poet',
    'screenwriter',
    'critic',
    'researcher',  # Added for academic topics
    'educator',    # Added for educational content
    'analyst'      # Added for technical/business topics
]

TONE_STYLES = [
    'funny',
    'serious',
    'dramatic',
    'sarcastic',
    'critical',
    'mysterious',
    'emotional',
    'neutral',
    'educational', # Added for learning content
    'technical',   # Added for complex topics
    'casual'       # Added for conversational style
]

WRITING_STYLES = [
    'factual',    # Focus on facts and data
    'relatable',  # Use real-world examples
    'analytical', # Break down complex concepts
    'narrative',  # Tell a story
    'practical',  # Focus on actionable insights
    'balanced'    # Present multiple viewpoints
]

# Define topic categories
TOPIC_CATEGORIES = {
    'general': {
        'description': 'General topics without specific categorization',
        'prompt_emphasis': 'Provide a balanced, comprehensive overview'
    },
    'technical': {
        'description': 'Technical and scientific topics',
        'prompt_emphasis': 'Focus on accuracy and technical details'
    },
    'creative': {
        'description': 'Creative and artistic topics',
        'prompt_emphasis': 'Emphasize creative expression and artistic elements'
    },
    'educational': {
        'description': 'Educational and learning topics',
        'prompt_emphasis': 'Focus on clear explanations and learning outcomes'
    },
    'business': {
        'description': 'Business and professional topics',
        'prompt_emphasis': 'Emphasize practical applications and professional context'
    }
}

def init_gemini(model_name='gemini-2.0-flash-exp', api_key=None):
    if model_name not in AVAILABLE_MODELS:
        raise ValueError(f"Model {model_name} not supported")
    
    if not api_key:
        api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        raise ValueError("API key not found")
        
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name)

def get_topic_category(topic: str) -> str:
    """
    Determine the most likely category for a given topic based on keywords.
    
    Args:
        topic (str): The topic to categorize
        
    Returns:
        str: The determined category name
    """
    # Convert topic to lowercase for case-insensitive matching
    topic_lower = topic.lower()
    
    # Define keyword mappings for each category
    category_keywords = {
        'technical': ['programming', 'technology', 'science', 'engineering', 'math', 'data', 'algorithm', 'system'],
        'creative': ['art', 'music', 'writing', 'design', 'creative', 'story', 'poetry', 'fiction'],
        'educational': ['learning', 'education', 'teaching', 'study', 'academic', 'school', 'university', 'course'],
        'business': ['business', 'marketing', 'finance', 'management', 'strategy', 'entrepreneurship', 'startup']
    }
    
    # Check for keyword matches
    for category, keywords in category_keywords.items():
        if any(keyword in topic_lower for keyword in keywords):
            return category
            
    # Default to general if no specific category is matched
    return 'general'