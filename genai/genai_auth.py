import msal
import jwt
import os
from dotenv import load_dotenv, find_dotenv
import json
import requests
import pprint
import sseclient
import atexit

_ = load_dotenv(find_dotenv()) # read local .env file

session = requests.Session()
cache = msal.SerializableTokenCache()

AZURE_AUTHORITY = os.environ['AZURE_AUTHORITY']
AZURE_CLIENT_ID = os.environ['AZURE_CLIENT_ID']
AZURE_SCOPE = os.environ['AZURE_SCOPE']


if os.path.exists("my_cache.bin"):
    cache.deserialize(open("my_cache.bin", "r").read())
else:
    atexit.register(lambda:
        open("my_cache.bin", "w").write(cache.serialize())
        if cache.has_state_changed else None
        )

_msal_auth = msal.PublicClientApplication(
        client_id=AZURE_CLIENT_ID,
        authority=AZURE_AUTHORITY,
        token_cache=cache
)  

token_meta = _msal_auth.acquire_token_silent(scopes=[AZURE_SCOPE])
token = token_meta['access_token']

decoded = jwt.decode(token, options={"verify_signature": False})

headers = {
    'accept': 'application/json',
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json',
}
# Get the metadata for all the LLMs available
# model_names = requests.get('https://chat.int.bayer.com/api/v1/models', headers=headers)

# Pick a model
# model = model_names.json()[0]["model"]

json_data = {
    'messages': [
        {
            'role': 'system',
            'content': 'You are ChatGPT, a large language model trained by OpenAI. follow instructions carefully. Respond using markdown.',
        },
        {
            'role': 'user',
            'content': 'Hello world!',
        },
    ],
    'model': 'deepmind/meta-llama-3-8b-instruct',
    'temperature': 0,
    'stream': True,
    'regenerate': False,
}
prediction = session.post('https://chat.int.bayer.com/api/v1/chat/completions', headers=headers, json=json_data, stream=True) # 

# print(prediction.text)

client = sseclient.SSEClient(prediction)
for event in client.events():
    data = json.loads(event.data)['choices'][0]['delta'].get('content')
    if data:
        print(data,end="")
    else:
        break

    