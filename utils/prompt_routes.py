from flask import Blueprint, request, jsonify
from .prompt_manager import PromptManager

prompt_routes = Blueprint('prompt_routes', __name__)
prompt_manager = PromptManager()

@prompt_routes.route('/prompts', methods=['GET'])
def list_prompts():
    prompts = prompt_manager.list_prompts()
    return jsonify(prompts)

@prompt_routes.route('/prompts/<prompt_id>', methods=['GET'])
def get_prompt(prompt_id):
    prompt = prompt_manager.get_prompt(prompt_id)
    if prompt:
        return jsonify(prompt)
    return jsonify({'error': 'Prompt not found'}), 404

@prompt_routes.route('/prompts', methods=['POST'])
def create_prompt():
    data = request.json
    if not data or 'name' not in data or 'template' not in data or 'prompt_id' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    prompt = prompt_manager.save_prompt(
        data['prompt_id'],
        data['name'],
        data['template']
    )
    return jsonify(prompt), 201

@prompt_routes.route('/prompts/<prompt_id>', methods=['DELETE'])
def delete_prompt(prompt_id):
    if prompt_manager.delete_prompt(prompt_id):
        return jsonify({'message': 'Prompt deleted successfully'})
    return jsonify({'error': 'Prompt not found or cannot be deleted'}), 404