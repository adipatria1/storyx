from typing import Optional, List
from .config import init_gemini, AVAILABLE_MODELS, EXPERTISE_LEVELS, TONE_STYLES
from .prompt_builder import build_story_prompt
from .summary_generator import generate_summary
from .reference_processor import ReferenceProcessor
from .prompt_manager import PromptManager
import time
import json
import asyncio

class StoryGenerator:
    def __init__(self, model_name: str = 'gemini-2.0-flash-exp', api_key: Optional[str] = None):
        if model_name not in AVAILABLE_MODELS:
            raise ValueError(f"Model {model_name} not supported")
        self.model = init_gemini(model_name, api_key)
        self.model_name = model_name
        self.api_key = api_key
        self.reference_processor = ReferenceProcessor(self.model)
        self.prompt_manager = PromptManager()
        self.max_retries = 2  # Reduced retries for faster response
        self.chunk_size = 1500  # Smaller chunks for faster processing

    def validate_inputs(self, expertise: str, tone: str):
        if expertise not in EXPERTISE_LEVELS:
            raise ValueError(f"Expertise level '{expertise}' not supported")
        if tone not in TONE_STYLES:
            raise ValueError(f"Tone style '{tone}' not supported")

    async def safe_generate_content(self, prompt: str) -> str:
        """Asynchronously generate content with optimized retry logic."""
        for attempt in range(self.max_retries):
            try:
                response = self.model.generate_content(prompt)
                if not response or not response.text:
                    raise ValueError("Empty response received")
                return response.text.strip()
            except Exception as e:
                if attempt == self.max_retries - 1:
                    return json.dumps({"error": f"Failed to generate content: {str(e)}"})
                await asyncio.sleep(1)  # Reduced wait time
        
        return json.dumps({"error": "Failed to generate content after multiple attempts"})

    def process_long_content(self, content: str) -> str:
        """Process long content into smaller chunks."""
        if len(content) <= self.chunk_size:
            return content

        chunks = []
        current_chunk = ""
        paragraphs = content.split('\n\n')

        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) + 2 <= self.chunk_size:
                current_chunk += ('\n\n' + paragraph if current_chunk else paragraph)
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = paragraph

        if current_chunk:
            chunks.append(current_chunk)

        return '\n\n'.join(chunks[:3])  # Limit to first 3 chunks for faster response

    async def generate_story_chunk(
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
            
            # Skip YouTube processing in Vercel environment
            youtube_content = ""
            
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
            content = await self.safe_generate_content(prompt)
            
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

    async def generate_complete_story(
        self,
        topic: str,
        expertise: str,
        tone: str,
        context: Optional[str] = None,
        youtube_urls: Optional[List[str]] = None,
        total_parts: int = 2,  # Reduced default parts
        prompt_id: str = 'default',
        writing_style: str = 'balanced'
    ) -> str:
        story_parts = []
        summaries = []

        # Limit total parts in Vercel environment
        total_parts = min(total_parts, 2)

        for part in range(1, total_parts + 1):
            chunk = await self.generate_story_chunk(
                topic, expertise, tone, context, youtube_urls,
                part, total_parts, summaries, prompt_id, writing_style
            )
            
            try:
                error_check = json.loads(chunk)
                if isinstance(error_check, dict) and 'error' in error_check:
                    return json.dumps({"error": error_check['error']})
            except json.JSONDecodeError:
                story_parts.append(chunk)

            if part < total_parts:
                summary = await self.safe_generate_content(f"Summarize briefly: {chunk}")
                if not summary.startswith('{"error"'):
                    summaries.append(summary)
                await asyncio.sleep(1)

        return "\n\n".join(story_parts)
