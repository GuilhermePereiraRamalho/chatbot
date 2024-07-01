from openai import OpenAI
from dotenv import load_dotenv
import os
from time import sleep
from helpers import *

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = "gpt-4o"

policies_ecomart = load('data/Policies_Ecomart.txt')
data_ecomart = load('data/Data_Ecomart.txt')
products_ecomart = load('data/Products_Ecomart.txt')

def select_document(openai_response):
    if "policies" in openai_response:
        return data_ecomart + "\n" + policies_ecomart
    elif "products" in openai_response:
        return data_ecomart + "\n" + products_ecomart
    else:
        return data_ecomart

def select_context(user_message):
    system_prompt = f"""
        The company EcoMart has three main documents detailing different aspects of the business:

        #Document 1: "\n{data_ecomart}"\n"

        Document 2: "\n{policies_ecomart}"\n"

        Document 3: "\n{products_ecomart}"\n"

        Evaluate the user prompt and return the most suitable document to use in the context of the response.
        Return 'data' for Document 1, 'policies' for Document 2, and 'products' for Document 3.
    """
    response = client.chat.completions.create(
    model=model,
    messages=[
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content" : user_message
        }
    ],
    temperature=1,
    )

    context = response.choices[0].message.content.lower()

    return context
