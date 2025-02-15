from flask import Blueprint, jsonify
from .prompt_manager import PromptManager

prompt_preview = Blueprint('prompt_preview', __name__)
prompt_manager = PromptManager()

@prompt_preview.route('/prompts/<prompt_id>', methods=['GET'])
def get_prompt_preview(prompt_id):
    prompt = prompt_manager.get_prompt(prompt_id)
    if prompt:
        return jsonify(prompt)
    return jsonify({'error': 'Prompt not found'}), 404