import os
from twilio.rest import Client
from dotenv import load_dotenv
load_dotenv()

client = Client()

from_whatsapp_number = 'whatsapp:+14155238886'
to_whatsapp_number = 'whatsapp:' + os.getenv('LETTY_NUMBER')

client.messages.create(
    from_=from_whatsapp_number,
    body="Welcome to the FINs WhatsApp Chatbot!",
    to=to_whatsapp_number)
