import os
from dotenv import load_dotenv, find_dotenv
import json
from tenacity import retry, wait_random_exponential, stop_after_attempt
from termcolor import colored  

from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import FunctionTool, QueryEngineTool
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings, Document

GPT_MODEL = "gpt-35-turbo"

# Initiation of the connection to the database and OpenAI
_ = load_dotenv(find_dotenv()) # read local .env filHow many sone

Settings.llm = OpenAI(model="gpt-3.5-turbo", temperature=0)
Settings.llm.api_base = os.environ['MYGEN_API']
Settings.llm.api_key  = os.environ['MYGEN_KEY']

documents = SimpleDirectoryReader(input_files = ["./data/bayer-annual-report-2023.pdf"]).load_data()
print(documents)

index = VectorStoreIndex.from_documents(documents)

query_engine = index.as_query_engine()

response = query_engine.query(
    "What was the total bayer's EBITDA of the 2023?"
)
print(response)

# # Define the agent
# def multiply(a: float, b: float) -> float:
#     """Multiply two numbers and returns the product"""
#     return a * b

# def add(a: float, b: float) -> float:
#     """Add two numbers and returns the sum"""
#     return a + b

# multiply_tool = FunctionTool.from_defaults(fn=multiply)
# add_tool = FunctionTool.from_defaults(fn=add)

# agent = ReActAgent.from_tools([multiply_tool, add_tool], llm=client, verbose=True)

# response = agent.chat("What is 20+(2*4)? Use a tool to calculate every step.")