from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
#Useful video on how ngrok works: https://www.youtube.com/watch?v=S1uExj7mMgM

app = Flask(__name__)

@app.route("/whatsapp", methods=['GET', 'POST'])
def whatsapp_reply():
    response = MessagingResponse()

    response.message("Thank you for contacting the FINs team via WhatsApp")

    return str(response)

if __name__ == "__main__":
    app.run(port=8000)