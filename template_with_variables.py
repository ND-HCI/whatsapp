import os
from twilio.rest import Client
from dotenv import load_dotenv
import json
load_dotenv()

client = Client()

from_whatsapp_number = 'whatsapp:+14155238886'
to_whatsapp_number = 'whatsapp:' + os.getenv('ANNALISA_NUMBER')

# Define content variables in JSON format
content_variables = {
    "1": "Added Sugars",
    "2": "added_sugars",
    "3": "added_sugars",
    "4": "Animal Meats",
    "5": "animal_meats",
    "6": "animal_meats",
    "7": "Saturated Fat",
    "8": "saturated_fat",
    "9": "saturated_fat",
    "10": "Sodium",
    "11": "sodium",
    "12": "sodium",
    "13": "Im done",
    "14": "done",
    "15": "done"
    }

print(json.dumps(content_variables))

# Use your approved template with variables
client.messages.create(
    content_sid=os.getenv("VARIABLE_TEST2"),
    from_=from_whatsapp_number,
    content_variables=json.dumps(content_variables),
    to=to_whatsapp_number
)

