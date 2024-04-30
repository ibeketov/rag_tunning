# Implementation of the function call to the database using the GenAPI. The function call is used to query the SQLite database with a provided SQL query. 
# The function call is executed by the assistant to answer user questions about music using the Chinook Music Database.
# https://docs.int.bayer.com/baychatgpt/tutorials/open-source_function_calling/#call-llm-to-get-a-response

import sqlite3
import os
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
import json
from tenacity import retry, wait_random_exponential, stop_after_attempt
from termcolor import colored  

GPT_MODEL = "gpt-35-turbo"

# Initiation of the connection to the database and OpenAI
_ = load_dotenv(find_dotenv()) # read local .env filHow many sone

client = OpenAI()
client.base_url = "https://chat.int.bayer.com/api/v1"
client.api_key  = os.environ['MYGEN_KEY']

#coneect to the database
try: 
    conn = sqlite3.connect("data/Chinook.db")
except:
    print("Failed to connect to the database.")
    conn = None

@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(messages, tools=None, tool_choice=None, model=GPT_MODEL):
    """Send a request to the OpenAI API to generate a chat completion."""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
        )
        return response
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e


def pretty_print_conversation(messages):
    """Print the conversation with colored text based on the role of the speaker."""
    role_to_color = {
        "system": "red",
        "user": "green",
        "assistant": "blue",
        "function": "magenta",
    }
    
    for message in messages:
        if message["role"] == "system":
            print(colored(f"system: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "user":
            print(colored(f"user: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "assistant" and message.get("function_call"):
            print(colored(f"assistant: {message['function_call']}\n", role_to_color[message["role"]]))
        elif message["role"] == "assistant" and not message.get("function_call"):
            print(colored(f"assistant: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "function":
            print(colored(f"function ({message['name']}): {message['content']}\n", role_to_color[message["role"]]))


def get_table_names(conn):
    """Return a list of table names."""
    if conn is None:
        return []
    table_names = []
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
    for table in tables.fetchall():
        table_names.append(table[0])
    return table_names


def get_column_names(conn, table_name):
    """Return a list of column names."""
    column_names = []
    columns = conn.execute(f"PRAGMA table_info('{table_name}');").fetchall()
    for col in columns:
        column_names.append(col[1])
    return column_names


def get_database_info(conn):
    """Return a list of dicts containing the table name and columns for each table in the database."""
    table_dicts = []
    for table_name in get_table_names(conn):
        columns_names = get_column_names(conn, table_name)
        table_dicts.append({"table_name": table_name, "column_names": columns_names})
    return table_dicts


def ask_database(conn, query):
    """Function to query SQLite database with a provided SQL query."""
    try:
        results = str(conn.execute(query).fetchall())
    except Exception as e:
        results = f"query failed with error: {e}"
    return results

def execute_function_call(message):
    if message.tool_calls[0].function.name == "ask_database":
        query = json.loads(message.tool_calls[0].function.arguments)["query"]
        results = ask_database(conn, query)
    else:
        results = f"Error: function {message.tool_calls[0].function.name} does not exist"
    return results

def main():    
    database_schema_dict = get_database_info(conn)

    database_schema_string = "\n".join(
        [
            f"Table: {table['table_name']}\nColumns: {', '.join(table['column_names'])}"
            for table in database_schema_dict
        ]
    )

    # Define the tool to be used in the chat completion
    tools = [
        {
            "type": "function",
            "function": {
                "name": "ask_database",
                "description": "Use this function to answer user questions about music. Input should be a fully formed SQL query.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": f"""
                                    SQL query extracting info to answer the user's question.
                                    SQL should be written using this database schema:
                                    {database_schema_string}
                                    The query should be returned in plain text, not in JSON.
                                    """,
                        }
                    },
                    "required": ["query"],
                },
            }
        }
    ]

    # Example conversation
    messages = []
    messages.append({"role": "system", "content": "Answer user questions by generating SQL queries against the Chinook Music Database."})
    messages.append({"role": "user", "content": "Hi, who are the top 5 artists by number of tracks?"})
    chat_response = chat_completion_request(messages, tools)
    assistant_message = chat_response.choices[0].message
    print(assistant_message)
    assistant_message.content = str(assistant_message.tool_calls[0].function)
    messages.append({"role": assistant_message.role, "content": assistant_message.content})
    if assistant_message.tool_calls:
        results = execute_function_call(assistant_message)
        messages.append({"role": "function", "tool_call_id": assistant_message.tool_calls[0].id, "name": assistant_message.tool_calls[0].function.name, "content": results})
    pretty_print_conversation(messages)

    messages.append({"role": "user", "content": "What is the name of the album with the most tracks?"})
    chat_response = chat_completion_request(messages, tools)
    assistant_message = chat_response.choices[0].message
    assistant_message.content = str(assistant_message.tool_calls[0].function)
    messages.append({"role": assistant_message.role, "content": assistant_message.content})
    if assistant_message.tool_calls:
        results = execute_function_call(assistant_message)
        messages.append({"role": "function", "tool_call_id": assistant_message.tool_calls[0].id, "name": assistant_message.tool_calls[0].function.name, "content": results})
    pretty_print_conversation(messages)

    # print('Write your message to the bot and press ENTER:')
    # # while True:
    # user_input = input('You: ')
    # messages.append({"role": "user", "content": user_input})
    # chat_response = chat_completion_request(messages, tools)
    # assistant_message = chat_response.choices[0].message
    # assistant_message.content = str(assistant_message.tool_calls[0].function)
    # messages.append({"role": assistant_message.role, "content": assistant_message.content})
    # if assistant_message.tool_calls:
    #     results = execute_function_call(assistant_message)
    #     messages.append({"role": "function", "tool_call_id": assistant_message.tool_calls[0].id, "name": assistant_message.tool_calls[0].function.name, "content": results})
    # pretty_print_conversation(messages)

# Close the connection to the database    
    conn.close()


if __name__ == "__main__":
    main()
