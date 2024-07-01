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

def create_id_list():
    file_id_list = []

    file_data = client.files.create(
        file=open("data/Data_Ecomart.txt", "rb"),
        purpose="assistants"
    )
    file_id_list.append(file_data.id)

    file_policies = client.files.create(
        file=open("data/Policies_Ecomart.txt", "rb"),
        purpose="assistants"
    )
    file_id_list.append(file_policies.id)

    file_products = client.files.create(
        file=open("data/Products_Ecomart.txt", "rb"),
        purpose="assistants"
    )
    file_id_list.append(file_products.id)

    return file_id_list 

def get_json():
    filename = "assistants.json"

    if not os.path.exists(filename):
        thread_id = create_thread()
        file_id_list = create_id_list()
        assistant_id = create_assistant(file_id_list)
        data = {
            "assistant_id": assistant_id.id,
            "thread_id": thread_id.id,
            "file_ids": file_id_list
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

def create_assistant(file_ids=[]):
    assistant = client.beta.assistants.create(
        name="EcoMart Assistant",
        instructions=f"""
            You are a customer service chatbot for an e-commerce platform.
            You should only respond to questions related to the specified e-commerce data!
            Additionally, access the files associated with you and the thread to respond to questions.
        """,
        model=model,
        tools=my_tools,
        file_ids=file_ids
    )
    return assistant
