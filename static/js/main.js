// Initialize form elements with data from the server
async function initializeForm() {
    // Populate model select
    const modelSelect = document.getElementById('model');
    const models = {{ models|tojson|safe }};
    models.forEach(model => {
        const option = new Option(model, model);
        modelSelect.add(option);
    });

    // Populate expertise select
    const expertiseSelect = document.getElementById('expertise');
    const expertiseLevels = {{ expertise_levels|tojson|safe }};
    expertiseLevels.forEach(level => {
        const option = new Option(level, level);
        expertiseSelect.add(option);
    });

    // Populate tone select
    const toneSelect = document.getElementById('tone');
    const toneStyles = {{ tone_styles|tojson|safe }};
    toneStyles.forEach(style => {
        const option = new Option(style, style);
        toneSelect.add(option);
    });

    // Populate writing style select
    const writingStyleSelect = document.getElementById('writingStyle');
    const writingStyles = {{ writing_styles|tojson|safe }};
    writingStyles.forEach(style => {
        const option = new Option(style, style);
        writingStyleSelect.add(option);
    });

    // Load prompt templates
    await loadPrompts();
}

// Load available prompt templates
async function loadPrompts() {
    try {
        const response = await fetch('/prompts');
        const prompts = await response.json();
        const promptSelect = document.getElementById('promptTemplate');
        promptSelect.innerHTML = ''; // Clear existing options
        
        Object.entries(prompts).forEach(([id, prompt]) => {
            const option = new Option(prompt.name, id);
            promptSelect.add(option);
        });
    } catch (error) {
        showToast('Error loading prompt templates', 'error');
    }
}

// Add new YouTube URL input field
function addYouTubeField() {
    const container = document.getElementById('youtubeUrls');
    const newField = container.children[0].cloneNode(true);
    newField.querySelector('input').value = '';
    container.appendChild(newField);
}

// Form submission handler
document.getElementById('storyForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const generateBtn = document.getElementById('generateBtn');
    const generateBtnText = document.getElementById('generateBtnText');
    const generateSpinner = document.getElementById('generateSpinner');
    
    generateBtn.disabled = true;
    generateBtnText.textContent = 'Generating...';
    generateSpinner.classList.remove('hidden');

    const youtubeUrls = Array.from(document.querySelectorAll('#youtubeUrls input'))
        .map(input => input.value)
        .filter(url => url.trim() !== '');

    const formData = {
        topic: document.getElementById('topic').value,
        model: document.getElementById('model').value,
        expertise: document.getElementById('expertise').value,
        tone: document.getElementById('tone').value,
        context: document.getElementById('context').value,
        youtube_urls: youtubeUrls,
        total_parts: parseInt(document.getElementById('total_parts').value),
        prompt_id: document.getElementById('promptTemplate').value,
        writing_style: document.getElementById('writingStyle').value
    };

    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        document.getElementById('storyContent').textContent = data.story;
        document.getElementById('storyOutput').classList.remove('hidden');

        showToast('Story generated successfully!');

    } catch (error) {
        showToast(error.message || 'An error occurred', 'error');
    } finally {
        generateBtn.disabled = false;
        generateBtnText.textContent = 'Generate Story';
        generateSpinner.classList.add('hidden');
    }
});

// Download functionality
document.getElementById('downloadBtn').addEventListener('click', async () => {
    const downloadBtn = document.getElementById('downloadBtn');
    const downloadSpinner = document.getElementById('downloadSpinner');
    const story = document.getElementById('storyContent').textContent;
    
    try {
        downloadBtn.disabled = true;
        downloadSpinner.classList.remove('hidden');
        
        const response = await fetch('/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ story })
        });

        if (!response.ok) {
            throw new Error('Download failed');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'generated_story.txt';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();

    } catch (error) {
        showToast(error.message || 'Download failed', 'error');
    } finally {
        downloadBtn.disabled = false;
        downloadSpinner.classList.add('hidden');
    }
});

// Toast Notifications
function showToast(message, type = 'success') {
    Toastify({
        text: message,
        duration: 3000,
        gravity: "top",
        position: "right",
        backgroundColor: type === 'success' ? "#10B981" : "#EF4444"
    }).showToast();
}

// Initialize form on page load
document.addEventListener('DOMContentLoaded', initializeForm);