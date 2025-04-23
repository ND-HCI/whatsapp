import os
import time
import json
import re
from utils.twilio_utils import send_whatsapp_message
from utils.template_config import TEMPLATE_CONTENT_VARIABLES
from utils.load_excel import PRODUCTS

# Dictionary to track user state
USER_SESSIONS = {}

def initialize_user_session(user_id):
   """Initialize a new user session and send welcome/build list message."""
   # Send the welcome message
   send_whatsapp_message(os.getenv("WELCOME_MESSAGE"), user_id)
   time.sleep(2)  # Pause for 2 seconds
   content_variables = json.dumps({
        "1": "Sodium",
        "2": "sodium",
        "3": "Added Sugars",
        "4": "added sugars",
        "5": "Saturated Fats",
        "6": "saturated fats",
        "7": "Animal Proteins",
        "8": "animal proteins",
        "9": "Done",
        "10": "done"
    })  # “4”: “Stuff”,

   # Send the build list message
   send_whatsapp_message(os.getenv("list_selector_5_dietary_goals"), user_id, content_variables)
#    send_whatsapp_message(os.getenv("BUILD_LIST"), user_id)


   # Initialize session data
   USER_SESSIONS[user_id] = {
        "list_items": [],                # Store list items
        "awaiting_list": False,          # Track whether user is entering list items
        "awaiting_options": False, 
        "get_recs": False,
        "add_remove_list": False, 
        "remove_items": False, 
        "add_items": False,
        "less_of_dietary_preferences": {
            "remaining": ["Sodium", "Saturated Fat", "Added Sugars", "Animal Proteins"],
            "selected": [],
            "in_progress": True
        },
        "more_of_dietary_preferences": {
            "remaining": ["Fruits", "Vegetables", "Fish", "Whole Grains", "Plant Proteins"],
            "selected": [],
            "in_progress": False
        }
    }


def handle_user_message(user_id, user_message):
   user_message = user_message.strip()  # Clean up input
  
   if user_id not in USER_SESSIONS:
       initialize_user_session(user_id)
       return

   if USER_SESSIONS[user_id]["less_of_dietary_preferences"]:
       collect_dietary_info(user_id, user_message)
       return

   if USER_SESSIONS[user_id]["awaiting_list"]:
       handle_list_building(user_id, user_message)
       return
  
   if USER_SESSIONS[user_id]["awaiting_options"]:
       handle_options(user_id, user_message)
       return
   
   if USER_SESSIONS[user_id]["add_remove_list"]:
       handle_list_modification(user_id, user_message)
       return
   
   if USER_SESSIONS[user_id]["remove_items"]: 
       handle_add_items(user_id, user_message)
       return
       
   if USER_SESSIONS[user_id]["add_items"]: 
       handle_remove_items(user_id, user_message)
       return

# -------------------------------------------------------------------------------------------------------------

def collect_dietary_info(user_id, user_message):
   """
   Send user the dietary goals options and have them respond.
   Create function that will 
   """


def modify_dietary_info(user_id, user_message):
   """
   Send user the dietary goals options and have them respond.
   Create function that will 
   """


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
        # Inform the user about list modification mode
        send_whatsapp_message(os.getenv("LIST_MODIFICATION_MODE"), user_id)
        
        # Switch user back to list building mode
        USER_SESSIONS[user_id]["awaiting_options"] = False
        USER_SESSIONS[user_id]["add_remove_list"] = True


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
       image_link = product_row["Image"]
       product_link = product_row["Link"]

       # remove beginning of the url
       match = re.search(r"https://i5\.walmartimages\.com/([^/]+)", image_link)
       if match:
          product_id = match.group(1)  # Get the captured product ID
          print(f"Extracted product ID: {product_id}")
          content_variables = json.dumps({"{{1}}": product_id, "{{2}}": product_link, "{{3}}": image_link})
          # Send the WhatsApp message
          send_whatsapp_message(os.getenv("GET_RECS"), user_id, content_variables)
       
   elif normalized_message == "just save my list":
        user_list = USER_SESSIONS[user_id]["list_items"]
        print(f"Saving list for user {user_id}: {user_list}")

        #Send confirmation message using the Twilio template
        send_whatsapp_message(os.getenv("CONFIRMATION_SAVE_LIST"), user_id)

        #Reset session or conclude the conversation
        USER_SESSIONS[user_id]["awaiting_options"] = False
        USER_SESSIONS[user_id]["awaiting_list"] = False
        USER_SESSIONS[user_id]["list_items"] = []  # Reset if you want a fresh start for next session
        send_whatsapp_message("Thank you! If you need further assistance, type 'start'.", user_id)
        #Send Message that says "List was saved" from the templates

def handle_list_modification(user_id, user_message):
        # Normalize the message by stripping, converting to lowercase, and removing special characters
    normalized_message = user_message.strip().lower()

   # Debugging: Print the received option
    print(f"User {user_id} selected option: '{normalized_message}'")

    user_list = USER_SESSIONS[user_id]["list_items"]
   
    list_string = ", ".join(user_list)  # Join the items in the list with commas

    print(f"User {user_id} list: {list_string}")

    list_items = {
        "1": list_string 
    }

    list_items=json.dumps(list_items)

    if normalized_message == "add item(s)":
        # Logic to handle adding/removing items
        # Inform the user about list modification mode
        send_whatsapp_message(os.getenv("ADD_ITEMS"), user_id, list_items)
        
        # Switch user back to list building mode
        USER_SESSIONS[user_id]["add_remove_list"] = False
        USER_SESSIONS[user_id]["add_items"] = True

    elif normalized_message == "remove item(s)":
        
        send_whatsapp_message(os.getenv("REMOVE_ITEMS"), user_id, list_items)
        
        # Switch user back to list building mode
        USER_SESSIONS[user_id]["add_remove_list"] = False
        USER_SESSIONS[user_id]["remove_items"] = True

    elif normalized_message == "go back":
        
        # Switch user back to list building mode
        USER_SESSIONS[user_id]["add_remove_list"] = False
        USER_SESSIONS[user_id]["awaiting_options"] = True

        send_whatsapp_message(os.getenv("OPTIONS"), user_id)


def handle_add_items(user_id, user_message):

    normalized_message = user_message.strip().lower().replace("’", "'")  # Replace curly with straight apostrophe

    if normalized_message == "i'm done":
        
        USER_SESSIONS[user_id]["add_items"] = False
        USER_SESSIONS[user_id]["awaiting_options"] = True  # Transition to options state
        user_list = USER_SESSIONS[user_id]["list_items"]

        print(f"Processing list for user {user_id}: {user_list}")

        # Send a confirmation message
        send_whatsapp_message(os.getenv("DONE_LIST"), user_id)
        time.sleep(2)  # Pause for 2 seconds
        #Sending next steps in the flow to view
        send_whatsapp_message(os.getenv("OPTIONS"), user_id)

    else:
    # Add the new item to the user's list
        USER_SESSIONS[user_id]["list_items"].append(normalized_message)


def handle_remove_items(user_id, user_message):
    
    normalized_message = user_message.strip().lower().replace("’", "'")

    user_list = USER_SESSIONS[user_id]["list_items"]
    
    # Normalize the list items (strip spaces, lower case, and handle curly apostrophes)
    normalized_list = [item.strip().lower().replace("’", "'") for item in user_list]

      # Replace curly with straight apostrophe

    if normalized_message == "i'm done":
        
        USER_SESSIONS[user_id]["add_items"] = False
        USER_SESSIONS[user_id]["awaiting_options"] = True  # Transition to options state
        user_list = USER_SESSIONS[user_id]["list_items"]

        print(f"Processing list for user {user_id}: {user_list}")

        # Send a confirmation message
        send_whatsapp_message(os.getenv("DONE_LIST"), user_id)
        time.sleep(2)  # Pause for 2 seconds
        #Sending next steps in the flow to view
        send_whatsapp_message(os.getenv("OPTIONS"), user_id)

    else:
        if normalized_message in normalized_list:
            index = normalized_list.index(normalized_message)  # Find the index of the first match
            item_to_remove = user_list[index]  # Get the actual item (not normalized)

            # Remove the first occurrence of the item from the original list
            USER_SESSIONS[user_id]["list_items"].remove(item_to_remove)
            print(user_list)

        else:
            print("Not in list")
            #We need a message here if it's not found in the list

