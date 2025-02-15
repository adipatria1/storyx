from typing import Optional, List
from .config import init_gemini, AVAILABLE_MODELS, EXPERTISE_LEVELS, TONE_STYLES
from .prompt_builder import build_story_prompt
from .summary_generator import generate_summary
from .reference_processor import ReferenceProcessor
from .prompt_manager import PromptManager
import time
import json

class StoryGenerator:
    def __init__(self, model_name: str = 'gemini-2.0-flash-exp', api_key: Optional[str] = None):
        if model_name not in AVAILABLE_MODELS:
            raise ValueError(f"Model {model_name} not supported")
        self.model = init_gemini(model_name, api_key)
        self.model_name = model_name
        self.api_key = api_key
        self.reference_processor = ReferenceProcessor(self.model)
        self.prompt_manager = PromptManager()

    def validate_inputs(self, expertise: str, tone: str):
        if expertise not in EXPERTISE_LEVELS:
            raise ValueError(f"Expertise level '{expertise}' not supported")
        if tone not in TONE_STYLES:
            raise ValueError(f"Tone style '{tone}' not supported")

    def safe_generate_content(self, prompt: str, max_retries: int = 3) -> str:
        """Safely generate content with retry logic and error handling."""
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                if not response or not response.text:
                    raise ValueError("Empty response received")
                return response.text.strip()
            except Exception as e:
                if attempt == max_retries - 1:
                    return json.dumps({"error": f"Failed to generate content: {str(e)}"})
                time.sleep(2)  # Wait before retrying
        
        return json.dumps({"error": "Failed to generate content after multiple attempts"})

    def process_long_content(self, content: str, max_length: int = 2000) -> str:
        """Process long content into manageable chunks."""
        if len(content) <= max_length:
            return content

        chunks = []
        current_chunk = ""
        paragraphs = content.split('\n\n')

        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) + 2 <= max_length:
                current_chunk += ('\n\n' + paragraph if current_chunk else paragraph)
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = paragraph

        if current_chunk:
            chunks.append(current_chunk)

        return '\n\n'.join(chunks)

    def generate_story_chunk(
        self,
        topic: str,
        expertise: str,
        tone: str,
        context: Optional[str] = None,
        youtube_urls: Optional[List[str]] = None,
        part_number: int = 1,
        total_parts: int = 1,
        previous_parts: list[str] = None,
        prompt_id: str = 'default',
        writing_style: str = 'balanced'
    ) -> str:
        try:
            self.validate_inputs(expertise, tone)
            
            # Process YouTube references if provided
            youtube_content = ""
            if youtube_urls:
                youtube_content = self.reference_processor.process_youtube_references(youtube_urls)
                if youtube_content and not youtube_content.startswith('Error'):
                    integration_prompt = f"""
                    Integrate the following reference material with the topic "{topic}":

                    Reference Material:
                    {youtube_content}

                    Create a comprehensive context that:
                    1. Combines insights from the reference material
                    2. Relates directly to the main topic
                    3. Preserves specific details and examples
                    4. Maintains technical accuracy
                    5. Incorporates expert perspectives

                    Format as additional context that enhances the main topic discussion.
                    """
                    
                    try:
                        integrated_content = self.safe_generate_content(integration_prompt)
                        if not integrated_content.startswith('{"error"'):
                            context = (f"{context}\n\n--- Additional References ---\n{integrated_content}"
                                     if context else integrated_content)
                    except Exception as e:
                        print(f"Error integrating YouTube content: {str(e)}")
            
            # Get custom prompt if specified
            custom_prompt = self.prompt_manager.get_prompt(prompt_id)
            if custom_prompt:
                prompt = build_story_prompt(
                    topic, expertise, tone, context,
                    part_number, total_parts, previous_parts,
                    custom_template=custom_prompt['template'],
                    writing_style=writing_style
                )
            else:
                prompt = build_story_prompt(
                    topic, expertise, tone, context,
                    part_number, total_parts, previous_parts,
                    writing_style=writing_style
                )

            # Generate content with safety checks
            content = self.safe_generate_content(prompt)
            
            # Check if there was an error
            try:
                error_check = json.loads(content)
                if isinstance(error_check, dict) and 'error' in error_check:
                    return error_check['error']
            except json.JSONDecodeError:
                # Not an error message, continue processing
                pass

            # Process long content if needed
            return self.process_long_content(content)

        except Exception as e:
            return json.dumps({"error": f"Error generating story part {part_number}: {str(e)}"})

    def generate_complete_story(
        self,
        topic: str,
        expertise: str,
        tone: str,
        context: Optional[str] = None,
        youtube_urls: Optional[List[str]] = None,
        total_parts: int = 3,
        prompt_id: str = 'default',
        writing_style: str = 'balanced'
    ) -> str:
        story_parts = []
        summaries = []

        for part in range(1, total_parts + 1):
            chunk = self.generate_story_chunk(
                topic, expertise, tone, context, youtube_urls,
                part, total_parts, summaries, prompt_id, writing_style
            )
            
            # Check if the chunk is an error message
            try:
                error_check = json.loads(chunk)
                if isinstance(error_check, dict) and 'error' in error_check:
                    return json.dumps({"error": error_check['error']})
            except json.JSONDecodeError:
                # Not an error message, continue processing
                story_parts.append(chunk)

            if part < total_parts:
                summary = generate_summary(chunk, self.model)
                summaries.append(summary)
                time.sleep(2)  # Add small delay between requests

        return "\n\n".join(story_parts)
