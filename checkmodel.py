# Save as check_models.py and run it
import os
import requests
from dotenv import load_dotenv

load_dotenv()

url = "https://api.groq.com/openai/v1/models"
headers = {"Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}"}

response = requests.get(url, headers=headers)
models = response.json()

for model in models["data"]:
    print(model["id"])