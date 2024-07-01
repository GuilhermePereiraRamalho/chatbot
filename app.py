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
from vision_ecomart import analyze_image
import uuid

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = "gpt-4o"

app = Flask(__name__)
CORS(app, resources={r"/chat": {"origins": "http://localhost:5000"}})
app.secret_key = 'alura'

assistant = get_json()
thread_id = assistant["thread_id"]
assistant_id = assistant["assistant_id"]

STATUS_COMPLETED = "completed" 
STATUS_REQUIRES_ACTION = "requires_action" 

uploaded_image_path = None
UPLOAD_FOLDER = 'data'

def bot(prompt):
    global uploaded_image_path
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

            vision_response = ""
            if uploaded_image_path != None:
                vision_response = analyze_image(uploaded_image_path)
                vision_response += ". In the final response, provide details of the image description."
                os.remove(uploaded_image_path)
                uploaded_image_path = None

            client.beta.threads.messages.create(
                thread_id=thread_id,
                content= vision_response+prompt,
                role="user"
            )

            run = client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=assistant_id
            )

            while run.status != STATUS_COMPLETED:
                run = client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id
                )
                print(f'Status: {run.status}')

                if run.status == STATUS_REQUIRES_ACTION:
                    tools_triggered = run.required_action.submit_tool_outputs.tool_calls
                    triggered_tool_responses = []
                    for tool in tools_triggered:
                        function_name = tool.function.name
                        chosen_function = my_functions[function_name]
                        arguments = json.loads(tool.function.arguments)
                        print(arguments)
                        function_response = chosen_function(arguments)

                        triggered_tool_responses.append({
                            'tool_call_id': tool.id,
                            'output': function_response
                        })
                
                    run = client.beta.threads.runs.submit_tool_outputs(
                        thread_id = thread_id,
                        run_id = run.id,
                        tool_outputs=triggered_tool_responses
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

@app.route('/upload_image', methods=['POST'])
def upload_image():
    global uploaded_image_path
    if 'image' in request.files:
        uploaded_image = request.files['image']
        
        filename = str(uuid.uuid4()) + os.path.splitext(uploaded_image.filename)[1]
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        uploaded_image.save(file_path)
        uploaded_image_path = file_path

        return 'Image received successfully!', 200
    return 'No file uploaded', 400

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
