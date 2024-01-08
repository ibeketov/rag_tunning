import os
import openai
from dotenv import load_dotenv, find_dotenv

from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv()) # read local .env file

openai.api_key  = os.environ['OPENAI_API_KEY']

client = openai.OpenAI()

def get_completion(prompt, model="gpt-3.5-turbo", temperature=0):
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature
    )
    return response.choices[0].message.content

messages =  [  
{'role':'system', 
 'content':"""You are an assistant who\
 responds in the style of Dr Seuss."""},    
{'role':'user', 
 'content':"""write me a very short poem\
 about a happy carrot"""},  
] 


response = get_completion(messages, temperature=1)
print(response)

# ChatCompletion(id='chatcmpl-8VJbdBqPLppzzI9Xw7d2tUYgo3QOr', choices=[Choice(finish_reason='stop', index=0, message=ChatCompletionMessage(content='This is a test.', role='assistant', function_call=N
# one, tool_calls=None))], created=1702474225, model='gpt-3.5-turbo-0613', object='chat.completion', system_fingerprint=None, usage=CompletionUsage(completion_tokens=5, prompt_tokens=12, total_tokens=17)) 