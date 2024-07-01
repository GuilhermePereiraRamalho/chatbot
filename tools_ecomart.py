from flask import Flask,render_template, request, Response
from openai import OpenAI
from dotenv import load_dotenv
import os
from time import sleep
from helpers import *
from select_document import *
from select_persona import *

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = "gpt-4o"

my_tools = [
    {'type': 'file_search'},
    {
        "type": "function",
        "function": {
            "name": "validate_promo_code",
            "description": "Validate a promotional code based on the company's Discounts and Promotions guidelines",
            "parameters": {
            "type": "object",
            "properties": {
                "code": {
                "type": "string",
                "description": "The promotional code, in the format CUPOM_XX. For example: CUPOM_ECO."
                },
                "validity": {
                "type": "string",
                "description": "The validity of the coupon, if valid and compliant with policies. Format: DD/MM/YYYY."
                }
            },
            "required": ["code", "validity"]
            }
        }
    }
]

def validate_promo_code(arguments):
    code = arguments.get("code")
    validity = arguments.get("validity")

    return f"""
    
    # Response Format
    
    {code} with validity: {validity}. 
    Also, indicate whether it is valid or not for the user.

    """

my_functions = {
    "validate_promo_code": validate_promo_code,
}