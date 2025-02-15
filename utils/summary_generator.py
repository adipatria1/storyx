def generate_summary(text: str, model) -> str:
    try:
        summary_prompt = f"""
        Create a concise summary (maximum 400 words) of the following content segment.
        Focus on:
        1. Key points and main arguments presented
        2. New concepts or perspectives introduced
        3. Important conclusions or insights
        4. Areas set up for future discussion
        
        Do NOT include:
        - Basic background information
        - Previously covered material
        - General context already established
        
        Content to summarize:
        {text}
        
        Provide a focused summary that highlights the unique contributions of this segment and sets up for the next part.
        """
        summary = model.generate_content(summary_prompt).text
        return summary
    except Exception as e:
        return f"Summary unavailable: {str(e)}"