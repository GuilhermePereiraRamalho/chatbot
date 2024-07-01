from openai import OpenAI
from dotenv import load_dotenv
import os
from time import sleep
from helpers import encode_image

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = "gpt-4o"

def analyze_image(image_path):
    prompt = """
        Assume you are a chatbot assistant and the user is likely sending a photo of
        a product. Analyze it, and if it is a defective product, provide a report. Assume you know and processed the image with Vision and the response will be formatted accordingly.

        # RESPONSE FORMAT
       
        My analysis for the image consists of: Report with indications of the defect or description of the product (if no defect)

        ## Describe the image
        put the description here
    """
    image_base64 = encode_image(image_path)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        max_tokens=300,
    )
    return response.choices[0].message.content

print(analyze_image("data/caneca_quebrada.jpg"))