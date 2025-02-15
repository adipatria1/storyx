from typing import List
from .youtube_extractor import extract_video_id, get_video_content

class ReferenceProcessor:
    def __init__(self, model):
        self.model = model
    
    def process_youtube_references(self, urls: List[str]) -> str:
        """Process multiple YouTube URLs and combine their content."""
        if not urls:
            return ""
            
        combined_content = []
        
        for url in urls:
            content = get_video_content(url)
            if not content.startswith('Error'):
                combined_content.append(content)
        
        if not combined_content:
            return ""
            
        # First, analyze each video's content separately
        analyzed_contents = []
        for content in combined_content:
            analysis_prompt = f"""
            Analyze this YouTube video content in detail:

            {content}

            Extract and preserve:
            1. Main points and key information
            2. Specific examples and data
            3. Technical details and explanations
            4. Expert opinions and insights
            5. Unique perspectives and approaches
            6. Real-world applications
            7. Case studies and demonstrations

            Format as a detailed analysis that maintains all specific information.
            """
            
            try:
                analysis = self.model.generate_content(analysis_prompt).text
                analyzed_contents.append(analysis)
            except Exception as e:
                print(f"Error analyzing video content: {str(e)}")
                continue
        
        if not analyzed_contents:
            return ""
        
        # Then, combine and structure all analyzed content
        combination_prompt = f"""
        Combine and structure these analyzed contents into a comprehensive reference:

        {'\n\n---\n\n'.join(analyzed_contents)}

        Create a unified knowledge base that:
        1. Preserves all specific information from each source
        2. Maintains technical accuracy and details
        3. Retains expert insights and unique perspectives
        4. Keeps all examples and case studies
        5. Organizes information logically
        6. Eliminates redundancy while keeping unique points
        7. Maintains the context and depth of each source

        Format as a detailed reference that can enhance the main topic discussion.
        """
        
        try:
            structured_content = self.model.generate_content(combination_prompt).text
            return structured_content
        except Exception as e:
            return f"Error processing references: {str(e)}"