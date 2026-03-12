KG_PROMPT = """
You are a knowledge graph extractor.

From the text below, extract factual knowledge as triples.
Use the format:
[["subject", "relation", "object"], ["subject", "relation", "object"], ...]

Rules:
- Subjects and objects must be concise nouns
- Relations must be verbs or verb phrases
- No explanations
- Only extract explicit facts
- Return ONLY the list of lists format

Text:
{text}
"""

import ollama
import re
import os
from dotenv import load_dotenv
load_dotenv()

def extract_triples_from_chunk(text_chunk: str):
    api_key = os.getenv("OLLAMA_API_KEY")
    host = "https://ollama.com"
    headers = {'Authorization': f'Bearer {api_key}'} if api_key else {}
    
    client = ollama.Client(host=host, headers=headers)
    
    response = client.chat(
        model='gpt-oss:120b', # Or any other suitable model available on Ollama cloud
        messages=[
            {"role": "system", "content": "You extract knowledge graph triples in a list of lists format."},
            {"role": "user", "content": KG_PROMPT.format(text=text_chunk)}
        ],
        options={'temperature': 0}
    )

    content = response['message']['content']
    import json
    try:
        # Try to parse the content as JSON directly
        triples = json.loads(content)
        if isinstance(triples, list):
            return triples
    except:
        pass

    # Fallback to regex if LLM doesn't return pure JSON or uses a different format
    triples = []
    for line in content.split("\n"):
        match = re.search(r'\["(.*?)",\s*"(.*?)",\s*"(.*?)"\]', line)
        if not match:
            # Also try the old parenthetical format just in case
            match = re.search(r"\((.*?),\s*(.*?),\s*(.*?)\)", line)
        
        if match:
            triples.append([
                match.group(1).strip().strip('"'),
                match.group(2).strip().strip('"'),
                match.group(3).strip().strip('"')
            ])

    return triples
