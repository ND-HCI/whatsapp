import os
from twilio.rest import Client

def send_whatsapp_message(content_sid, recipient, content_variables=None):
    client = Client()
    from_whatsapp_number = 'whatsapp:+14155238886'

    # Strip 'whatsapp:' prefix if present
    if recipient.startswith('whatsapp:'):
            recipient = recipient.replace('whatsapp:', '')

    to_whatsapp_number = f'whatsapp:{recipient}'

    print("Sending WhatsApp message:")
    print(f"To: {to_whatsapp_number}")

    client.messages.create(
        content_sid=content_sid,
        from_=from_whatsapp_number,
        to=to_whatsapp_number,
        content_variables=content_variables
        )