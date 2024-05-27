import os
import openai
from dotenv import load_dotenv, find_dotenv

from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv()) # read local .env file

MYGEN_API = os.environ['MYGEN_API']
MYGEN_KEY = os.environ['MYGEN_KEY']

client = openai.OpenAI(
    base_url=MYGEN_API,
    api_key = MYGEN_KEY
    )

response = client.embeddings.create(
    input="Your text string goes here", #optionally, you can also pass a list of strings
    model="text-embedding-3-small"
)

print(response.data[0].embedding[:10]) # print the first 10 elements of the embedding