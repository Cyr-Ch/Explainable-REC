import os
from openai import OpenAI

def _load_env_file():
    """Load environment variables from .env file if it exists"""
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key and value:
                        os.environ[key] = value

# Load .env file when module is imported
_load_env_file()

class LLM:
    def __init__(self, model='gpt-4o-mini'):
        # Make sure .env is loaded
        _load_env_file()
        api_key = os.getenv('OPENAI_API_KEY')
        self.model = model
        self.client = OpenAI(api_key=api_key) if api_key else None
    def complete(self, prompt, temperature=0.0, max_tokens=256):
        if self.client is None: return ''
        r=self.client.chat.completions.create(model=self.model, messages=[{'role':'user','content':prompt}], temperature=temperature, max_tokens=max_tokens)
        return r.choices[0].message.content or ''
