# test_embeddings.py
from openai import AzureOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-08-01-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

try:
    response = client.embeddings.create(
        input="Prueba de embedding",
        model="civic-chatbot-embeddings"
    )
    print("✅ Azure OpenAI funciona!")
    print(f"Embedding dimension: {len(response.data[0].embedding)}")
    print(f"Primeros 5 valores: {response.data[0].embedding[:5]}")
except Exception as e:
    print(f"❌ Error: {e}")
