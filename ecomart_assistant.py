from openai import OpenAI
from dotenv import load_dotenv
import os
from time import sleep
from helpers import *
from select_persona import *
import json
from tools_ecomart import *

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = "gpt-4o"
context = load('data/ecomart.txt')

def create_vector_store():
    vector_store = client.beta.vector_stores.create(name='Ecomart Vector Store')

    file_paths = [
        'data/Data_Ecomart.txt',
        'data/Policies_Ecomart.txt',
        'data/Products_Ecomart.txt'
    ]
    file_streams = [open(path, 'rb') for path in file_paths]

    client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id,
        files=file_streams
    )

    return vector_store

def get_json():
    filename = "assistants.json"

    if not os.path.exists(filename):
        vector_store = create_vector_store()
        thread = create_thread(vector_store)
        assistant = create_assistant(vector_store)

        data = {
            'assistant_id': assistant.id,
            'vector_store_id': vector_store.id,
            'thread_id': thread.id
        }

        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print("File 'assistants.json' successfully created.")

    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print("File 'assistants.json' not found.")

def create_thread(vector_store):
    return client.beta.threads.create(
        tool_resources={
            'file_search': {
                'vector_store_ids': [vector_store.id]
            }
        }
    )

def create_assistant(vector_store):
    assistant = client.beta.assistants.create(
        name="EcoMart Assistant",
        instructions=f"""
            You are a customer service chatbot for an e-commerce platform.
            You should only respond to questions related to the specified e-commerce data!
            Additionally, access the files associated with you and the thread to respond to questions.
        """,
        model=model,
        tools=my_tools,
        tool_resources={
            'file_search': {
                'vector_store_ids': [vector_store.id]
            }
        }
    )
    return assistant
