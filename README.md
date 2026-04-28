# Self-Improving-Pipeline
Static vs adaptive summarization using Groq API

The pipeline uses a Generator (Llama 3.1 8B), Evaluator (Llama 3.3 70B), and Improver that revises prompts based on feedback.

## Requirements

- Python 
- Groq API key 

## Setup

1. Get a free API key at https://console.groq.com/keys

2. Install the library: pip install groq

3. Open `Self-Improving-Pipeline.py` and replace:
```python
API_KEY = "YOUR_GROQ_API_KEY_HERE"

with your actual API key

4. Run: python Self-Improving-Pipeline.py

The script runs static and adaptive pipelines on three articles at temperature 0.7.
To change the temperature replace 0.7 to 0.9.

## That's it.
