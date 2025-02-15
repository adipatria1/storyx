from typing import Dict, Optional
import json
import os

class PromptManager:
    def __init__(self):
        self.prompts_file = 'data/custom_prompts.json'
        self.default_prompts = {
            'default': {
                'name': 'Default Prompt',
                'template': '''
                Generate part {part_number} of {total_parts} discussing this topic: {topic}
                Category: {topic_category}
                {context_text}
                {previous_context}
                
                Writing Guidelines:
                - Write as a {expertise}: {expertise_instructions}
                - Use a {tone} tone: {tone_instructions}
                
                Category-Specific Guidelines:
                {category_instructions}
                
                General Requirements:
                - Focus on accuracy and relevance
                - Include specific examples and references
                - Consider multiple perspectives
                - Support statements with evidence
                - Address potential questions or concerns
                - Provide practical insights when applicable
                
                Structure Requirements:
                - Minimum length: 4000 characters
                - Use clear paragraphs and transitions
                - Include relevant data when applicable
                - Balance theory and practice
                - Maintain professional yet accessible language
                - Format for easy reading and comprehension
                '''
            }
        }
        self._ensure_data_directory()
        self.load_prompts()

    def _ensure_data_directory(self):
        os.makedirs('data', exist_ok=True)
        if not os.path.exists(self.prompts_file):
            with open(self.prompts_file, 'w') as f:
                json.dump(self.default_prompts, f, indent=2)

    def load_prompts(self) -> Dict:
        try:
            with open(self.prompts_file, 'r') as f:
                return json.load(f)
        except Exception:
            return self.default_prompts

    def save_prompt(self, prompt_id: str, name: str, template: str) -> Dict:
        prompts = self.load_prompts()
        prompts[prompt_id] = {
            'name': name,
            'template': template
        }
        with open(self.prompts_file, 'w') as f:
            json.dump(prompts, f, indent=2)
        return prompts[prompt_id]

    def get_prompt(self, prompt_id: str) -> Optional[Dict]:
        prompts = self.load_prompts()
        return prompts.get(prompt_id)

    def delete_prompt(self, prompt_id: str) -> bool:
        if prompt_id == 'default':
            return False
        prompts = self.load_prompts()
        if prompt_id in prompts:
            del prompts[prompt_id]
            with open(self.prompts_file, 'w') as f:
                json.dump(prompts, f, indent=2)
            return True
        return False

    def list_prompts(self) -> Dict:
        return self.load_prompts()