KG_PROMPT = """
You are a knowledge graph extractor.

From the text below, extract factual knowledge as triples.
Use the format:
(subject, relation, object)

Rules:
- Subjects and objects must be concise nouns
- Relations must be verbs or verb phrases
- No explanations
- Only extract explicit facts

Text:
{text}
"""

import openai
import re
import os
from dotenv import load_dotenv
load_dotenv()

def extract_triples_from_chunk(text_chunk: str):
    llm = openai.OpenAI(api_key=os.getenv("OPEANAIKEY"))
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You extract knowledge graph triples."},
            {"role": "user", "content": KG_PROMPT.format(text=text_chunk)}
        ],
        temperature=0
    )

    content = response.choices[0].message["content"]

    triples = []
    for line in content.split("\n"):
        match = re.match(r"\((.*?),\s*(.*?),\s*(.*?)\)", line)
        if match:
            triples.append({
                "subject": match.group(1).strip(),
                "relation": match.group(2).strip(),
                "object": match.group(3).strip()
            })

    return triples
