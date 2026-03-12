import re
import json

def mock_extract_triples_from_content(content: str):
    # This matches the logic added to extracting_triplates.py
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