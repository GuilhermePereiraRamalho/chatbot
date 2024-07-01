from flask import Flask,render_template, request, Response
from openai import OpenAI
from dotenv import load_dotenv
import os
from time import sleep
from helpers import *
from flask_cors import CORS
from select_persona import *
from select_document import *
from ecomart_assistant import *

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = "gpt-4o"

app = Flask(__name__)
CORS(app, resources={r"/chat": {"origins": "http://localhost:5000"}})
app.secret_key = 'alura'

assistant = get_json()
thread_id = assistant["thread_id"]
assistant_id = assistant["assistant_id"]

def bot(prompt):
    max_attempts = 1
    retries = 0

    while True:
        try:
            personality = personas[select_persona(prompt)]

            client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=f"""
                Assume, from now on, the personality below.
                Ignore previous personalities.

                # Persona
                {personality}
                """
            )

            client.beta.threads.messages.create(
                thread_id=thread_id,
                content=prompt,
                role="user"
            )

            run = client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=assistant_id
            )

            while run.status != "completed":
                run = client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id
                )
            history = list(client.beta.threads.messages.list(thread_id=thread_id).data)
            response = history[0]
            return response
          
        except Exception as error:
            retries += 1
            if retries >= max_attempts:
                return "GPT error: %s" % error
            print('Communication error with OpenAI:', error)
            sleep(1)

@app.route("/chat", methods=["Post"])
def chat():
    prompt = request.json["msg"]
    response = bot(prompt)
    if isinstance(response, str):
        return response
    else:
        response_text = response.content[0].text.value
        return response_text

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug = True)
