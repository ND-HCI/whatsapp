import os
import time
import json
import re
from utils.twilio_utils import send_whatsapp_message
from utils.template_config import TEMPLATE_CONTENT_VARIABLES
from utils.load_excel import PRODUCTS


# Dictionary to track user state
USER_SESSIONS = {}


def handle_user_message(user_id, user_message):
   user_message = user_message.strip()  # Clean up input
  
   if user_id not in USER_SESSIONS:
       initialize_user_session(user_id)
       return


   if USER_SESSIONS[user_id]["awaiting_list"]:
       handle_list_building(user_id, user_message)
       return
  
   if USER_SESSIONS[user_id]["awaiting_options"]:
       handle_options(user_id, user_message)
       return


def initialize_user_session(user_id):
   """Initialize a new user session and send welcome/build list message."""
   # Send the welcome message
   send_whatsapp_message(os.getenv("WELCOME_MESSAGE"), user_id)
   time.sleep(2)  # Pause for 2 seconds


   # Send the build list message
   send_whatsapp_message(os.getenv("BUILD_LIST"), user_id)


   # Initialize session data
   USER_SESSIONS[user_id] = {
       "list_items": [],  # Store list items
       "awaiting_list": True,  # Track whether user is entering list items
       "awaiting_options": False, 
       "get_recs": False
   }


# -------------------------------------------------------------------------------------------------------------


def handle_list_building(user_id, user_message):
   """
   Handle user input while they are building their list.
   Manage adding items to the list or finalizing the list.
   """


   normalized_message = user_message.strip().lower().replace("’", "'")  # Replace curly with straight apostrophe


   # Debugging: Print the normalized message to verify input
   print(f"Received message from user {user_id}: '{normalized_message}'")


   if normalized_message == "i'm done":
       # Finalize the user's list
       USER_SESSIONS[user_id]["awaiting_list"] = False
       USER_SESSIONS[user_id]["awaiting_options"] = True  # Transition to options state
       user_list = USER_SESSIONS[user_id]["list_items"]


       # Process the list (e.g., save to a database or perform actions)
       print(f"Processing list for user {user_id}: {user_list}")


       # Send a confirmation message
       send_whatsapp_message(os.getenv("DONE_LIST"), user_id)
       time.sleep(2)  # Pause for 2 seconds
       #Sending next steps in the flow to view
       send_whatsapp_message(os.getenv("OPTIONS"), user_id)


   else:
       # Add the item that the user entered to the list called list_items
       USER_SESSIONS[user_id]["list_items"].append(user_message)


def handle_options(user_id, user_message):
   """
   Handle user response to options after finalizing the list.
   """
   normalized_message = user_message.strip().lower()


   # Debugging: Print the received option
   print(f"User {user_id} selected option: '{normalized_message}'")


   if normalized_message == "add/remove item":
       # Logic to handle adding/removing items
       print(f"Add Remove Item")


   elif normalized_message == "get recommendations":
       USER_SESSIONS[user_id]["awaiting_options"] = False
       USER_SESSIONS[user_id]["get_recs"] = True

       #get product list
       user_list = USER_SESSIONS[user_id]["list_items"]

       # get rec
       product_name = user_list[0].lower()
       print(product_name)

       # Search for the product in the PRODUCTS list
       product_row = next((p for p in PRODUCTS if p["Name"].lower() == product_name), None)

       # get item url
       product_link = product_row["Link"]

       # remove beginning of the url
       match = re.search(r"https://www\.walmart\.com/ip/([^/]+)", product_link)
       if match:
          product_id = match.group(1)  # Get the captured product ID
          print(f"Extracted product ID: {product_id}")
          content_variables = json.dumps({"{item}": product_id})
          # Send the WhatsApp message
          send_whatsapp_message(os.getenv("GET_RECS"), user_id, content_variables)
       
      
       # Here you will want to now set the handle_options to false, and then call then send a new whatsapp_message for the recommendation.


   elif normalized_message == "just save my list":


       print(f"Just Save My List")
       # Send Message that says "List was saved" from the templates
