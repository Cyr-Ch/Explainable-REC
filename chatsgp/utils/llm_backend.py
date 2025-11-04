import os
from openai import OpenAI
class LLM:
    def __init__(self, model='gpt-4o-mini'):
        self.model=model; self.client=OpenAI() if os.getenv('OPENAI_API_KEY') else None
    def complete(self, prompt, temperature=0.0, max_tokens=256):
        if self.client is None: return ''
        r=self.client.chat.completions.create(model=self.model, messages=[{'role':'user','content':prompt}], temperature=temperature, max_tokens=max_tokens)
        return r.choices[0].message.content or ''
