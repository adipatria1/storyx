from typing import Optional
from .config import get_topic_category

def build_story_prompt(
    topic: str,
    expertise: str,
    tone: str,
    context: Optional[str] = None,
    part_number: int = 1,
    total_parts: int = 1,
    previous_parts: list[str] = None,
    custom_template: Optional[str] = None,
    writing_style: str = 'balanced'  # Add default writing style
) -> str:
    topic_category = get_topic_category(topic)
    context_text = f"\nAdditional Context:\n{context}" if context else ""
    previous_context = ""
    if previous_parts and part_number > 1:
        previous_context = "\nPrevious parts summary:\n" + "\n".join(previous_parts)
    
    expertise_instructions = {
        'storyteller': 'Present the opinion in a narrative style with real-world examples',
        'novelist': 'Provide a detailed analysis with rich context and character perspectives',
        'journalist': 'Present factual, well-researched information with current events',
        'poet': 'Express the opinion through metaphors and emotional resonance',
        'screenwriter': 'Frame the opinion through dialogue and real-world scenarios',
        'critic': 'Analyze the topic with critical thinking and balanced perspectives',
        'researcher': 'Present in-depth analysis with academic rigor and citations',
        'educator': 'Explain concepts clearly with examples and learning objectives',
        'analyst': 'Provide data-driven insights and expert analysis'
    }

    tone_instructions = {
        'funny': 'Include humor while maintaining respect for serious topics',
        'serious': 'Maintain a professional and formal tone',
        'dramatic': 'Emphasize significant impacts and consequences',
        'sarcastic': 'Use clever observations while staying constructive',
        'critical': 'Provide balanced analysis with supporting evidence',
        'mysterious': 'Explore hidden aspects and implications',
        'emotional': 'Focus on human impact and personal experiences',
        'neutral': 'Present balanced viewpoints without bias',
        'educational': 'Focus on clear explanations and learning outcomes',
        'technical': 'Use precise terminology while remaining accessible',
        'casual': 'Maintain an approachable, conversational style'
    }

    category_instructions = {
        'factual': """
            - Focus on verified facts and data
            - Include statistics and research findings
            - Cite credible sources and studies
            - Present objective information
            - Minimize speculation and opinion
        """,
        'relatable': """
            - Use real-world examples and scenarios
            - Connect concepts to daily life
            - Share personal experiences and anecdotes
            - Make complex ideas accessible
            - Include practical applications
        """,
        'analytical': """
            - Break down complex concepts
            - Examine cause and effect relationships
            - Compare and contrast different aspects
            - Evaluate pros and cons
            - Provide detailed analysis
        """,
        'narrative': """
            - Tell a compelling story
            - Use character perspectives
            - Create engaging scenarios
            - Build narrative tension
            - Include descriptive details
        """,
        'practical': """
            - Focus on actionable insights
            - Provide step-by-step guidance
            - Include hands-on examples
            - Share best practices
            - Offer practical solutions
        """,
        'balanced': """
            - Present multiple viewpoints
            - Consider different perspectives
            - Weigh advantages and disadvantages
            - Provide balanced analysis
            - Include diverse examples
        """
    }

    # Use custom template if provided, otherwise use default
    if custom_template:
        prompt = custom_template.format(
            part_number=part_number,
            total_parts=total_parts,
            topic=topic,
            topic_category=topic_category,
            context_text=context_text,
            previous_context=previous_context,
            expertise=expertise,
            expertise_instructions=expertise_instructions.get(expertise, ''),
            tone=tone,
            tone_instructions=tone_instructions.get(tone, ''),
            category_instructions=category_instructions.get(writing_style, category_instructions['balanced'])
        )
    else:
        prompt = f"""
        Generate part {part_number} of {total_parts} discussing this topic: {topic}
        Category: {topic_category}
        {context_text}
        {previous_context}
        
        Writing Guidelines:
        - Write as a {expertise}: {expertise_instructions.get(expertise, '')}
        - Use a {tone} tone: {tone_instructions.get(tone, '')}
        
        Writing Style Guidelines:
        {category_instructions.get(writing_style, category_instructions['balanced'])}
        
        General Requirements:
        - Focus on accuracy and relevance
        - Include specific examples and references
        - Consider multiple perspectives
        - Support statements with evidence
        - Address potential questions or concerns
        - Provide practical insights when applicable
        - AVOID repeating information from previous parts
        - Build upon and expand previous discussions
        - Introduce new aspects and perspectives
        
        Structure Requirements:
        - Minimum length: 4000 characters
        - Use clear paragraphs and transitions
        - Include relevant data when applicable
        - Balance theory and practice
        - Maintain professional yet accessible language
        - Format for easy reading and comprehension
        """
    
    # Part-specific instructions to ensure progression
    if part_number == 1:
        prompt += """
        \nFor this opening part:
        - Introduce the topic and its significance
        - Provide essential background information
        - Present the foundational concepts
        - Outline the key aspects to be explored in later parts
        - Set up the framework for subsequent discussions
        """
    elif part_number == total_parts:
        prompt += """
        \nFor this final part:
        - Build upon previous discussions without repeating them
        - Explore advanced concepts and implications
        - Draw connections between all previous parts
        - Synthesize insights from earlier sections
        - Provide forward-looking conclusions
        - Offer unique perspectives and recommendations
        """
    else:
        section_focus = (part_number - 1) / (total_parts - 1)
        if section_focus < 0.33:
            prompt += """
            \nFor this early-middle part:
            - Expand on the foundational concepts
            - Introduce new perspectives and angles
            - Deepen the analysis with specific examples
            - Avoid repeating basic information
            - Bridge to more complex aspects
            """
        elif section_focus < 0.66:
            prompt += """
            \nFor this middle part:
            - Focus on complex interconnections
            - Present contrasting viewpoints
            - Analyze practical applications
            - Introduce advanced concepts
            - Avoid retreading earlier discussions
            """
        else:
            prompt += """
            \nFor this late-middle part:
            - Explore sophisticated implications
            - Present expert insights
            - Address emerging trends
            - Connect to broader contexts
            - Prepare for concluding insights
            """
    
    # Add a strong reminder about continuity
    prompt += """
    \nCRITICAL CONTINUITY REQUIREMENTS:
    - Each part must progress the discussion forward
    - Never repeat information from previous parts
    - Reference previous concepts only to build upon them
    - Introduce new aspects and perspectives in each part
    - Ensure a logical flow between parts
    - Maintain consistent terminology while exploring new areas
    """
        
    return prompt