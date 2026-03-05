import os
from ollama import Client
from dotenv import load_dotenv

load_dotenv()

def list_models():
    api_key = os.environ.get('OLLAMA_API_KEY')
    host = "https://ollama.com"
    headers = {'Authorization': f'Bearer {api_key}'} if api_key else {}
    
    client = Client(host=host, headers=headers)
    print(f"Connecting to host: {host}")
    try:
        models = client.list()
        print("Response type:", type(models))
        if isinstance(models, dict):
            print("Response keys:", models.keys())
            if 'models' in models and models['models']:
                print("First model sample:", models['models'][0])
                for m in models['models']:
                    # Try different possible keys for the model name
                    name = m.get('name') or m.get('model') or "Unknown"
                    print(f"- {name}")
        else:
            print("Response content:", models)
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    list_models()
