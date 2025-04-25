import sys
import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from utils.twilio_utils import send_whatsapp_message
from handlers.logic_handler import handle_user_message
import os

app = Flask(__name__)

@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    user_message = request.form.get('Body').strip().lower()
    user_id = request.form.get('From')  # User's WhatsApp number for tracking sessions

    print("Incoming message from:", user_id)
    print("Message content:", user_message)

    response = MessagingResponse()
    reply_message = handle_user_message(user_id, user_message)
    response.message(reply_message)

    return str(response)

if __name__ == "__main__":
    app.run(port=8005)