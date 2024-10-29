import os
from twilio.rest import Client
from dotenv import load_dotenv
load_dotenv()

client = Client()

from_whatsapp_number = 'whatsapp:+14155238886'
to_whatsapp_number = 'whatsapp:' + os.getenv('ANNALISA_NUMBER')

# Use your approved template
client.messages.create(
    content_sid=os.getenv("CARD_TEMPLATE"),
    from_=from_whatsapp_number,
    to=to_whatsapp_number,
)