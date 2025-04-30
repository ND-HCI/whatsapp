import os
import time
import json
import re
from utils.twilio_utils import send_whatsapp_message
from utils.load_excel import PRODUCTS

# Dictionary to track user state
USER_SESSIONS = {}

def initialize_user_session(user_id):
    """Initialize a new user session and send welcome/build list message."""
    send_whatsapp_message(os.getenv("WELCOME_MESSAGE"), user_id)
    time.sleep(4)  # Pause for 4 seconds instead of 2 seconds because lots of info to send

    USER_SESSIONS[user_id] = {
        "list_items": [],
        "awaiting_list": False,
        "awaiting_options": False,
        "get_recs": False,
        "add_remove_list": False,
        "remove_items": False,
        "add_items": False,
        "change_preferences": False,
        "less_of_dietary_preferences": {
            "remaining": ["Sodium", "Saturated Fats", "Added Sugars", "Animal Proteins"],
            "selected": [],
            "in_progress": True
        },
        "more_of_dietary_preferences": {
            "remaining": ["Fruits", "Vegetables", "Fish", "Whole Grains", "Plant Proteins"],
            "selected": [],
            "in_progress": False
        }
    }

    # Now separately send the dietary goals
    send_dietary_options_less_of(user_id)

def handle_user_message(user_id, user_message):
    user_message = user_message.strip()  # Clean up input
    
    if user_id not in USER_SESSIONS:
        initialize_user_session(user_id)
        return

    if USER_SESSIONS[user_id]["less_of_dietary_preferences"]["in_progress"]:
        collect_dietary_info_less_of(user_id, user_message)
        return

    if USER_SESSIONS[user_id]["more_of_dietary_preferences"]["in_progress"]:
        collect_dietary_info_more_of(user_id, user_message)
        return

    if USER_SESSIONS[user_id]["awaiting_list"]:
        handle_list_building(user_id, user_message)
        return

    if USER_SESSIONS[user_id]["awaiting_options"]:
        handle_options(user_id, user_message)
        return
    
    if USER_SESSIONS[user_id]["change_preferences"]:
        change_preferences(user_id, user_message)
        return

    if USER_SESSIONS[user_id]["add_remove_list"]:
        handle_list_modification(user_id, user_message)
        return

    if USER_SESSIONS[user_id]["remove_items"]: 
        handle_remove_items(user_id, user_message)
        return
        
    if USER_SESSIONS[user_id]["add_items"]: 
        handle_add_items(user_id, user_message)
        return

# -------------------------------------------------------------------------------------------------------------

def send_dietary_options_less_of(user_id):
    """Send updated dietary options to the user based on how many total choices (options + Done)."""
    session = USER_SESSIONS[user_id]
    remaining_options = session["less_of_dietary_preferences"]["remaining"]
    num_choices = len(remaining_options) + 1  # +1 for 'Done'

    if (len(remaining_options) + 1) <= 1:
        # If 1 or fewer real options left, skip and move on
        session["less_of_dietary_preferences"]["in_progress"] = False
        session["more_of_dietary_preferences"]["in_progress"] = True
        send_dietary_options_more_of(user_id)
        return

    # Build content variables
    content_variables = {}
    for idx, option in enumerate(remaining_options, start=1):
        content_variables[str(idx * 2 - 1)] = option
        content_variables[str(idx * 2)] = option.lower()

    # Always add Done at the end
    next_index = len(content_variables) + 1
    content_variables[str(next_index)] = "Done"
    content_variables[str(next_index + 1)] = "done"

    content_variables_json = json.dumps(content_variables)

    # Choose template based on TOTAL choices (real options + Done)
    if num_choices == 5:
        template_id = os.getenv("list_selector_5_dietary_goals")  # 5 options + Done
    elif num_choices == 4:
        template_id = os.getenv("list_selector_4_dietary_goals")  # 4 options + Done
    elif num_choices == 3:
        template_id = os.getenv("list_selector_3_dietary_goals")  # 3 options + Done
    elif num_choices == 2:
        template_id = os.getenv("list_selector_2_dietary_goals")  # 2 options + Done
    else:
        template_id = os.getenv("list_selector_2_dietary_goals")  # fallback safety

    print(content_variables_json)
    print(f"Template chosen: {template_id}")

    send_whatsapp_message(template_id, user_id, content_variables_json)

def collect_dietary_info_less_of(user_id, user_message):
    """Handle user input during dietary preferences selection."""
    normalized_message = user_message.strip().lower()

    session = USER_SESSIONS[user_id]
    remaining = session["less_of_dietary_preferences"]["remaining"]
    selected = session["less_of_dietary_preferences"]["selected"]

    # FIRST: check if user typed 'done'
    if normalized_message == "done":
        session["less_of_dietary_preferences"]["in_progress"] = False
        session["more_of_dietary_preferences"]["in_progress"] = True
        send_dietary_options_more_of(user_id)
        return

    # THEN: check if they picked an available option
    match = None
    for option in remaining:
        if normalized_message == option.lower():
            match = option
            break

    if match:
        selected.append(match)
        remaining.remove(match)

        print(f"User {user_id} selected '{match}'. Remaining options: {remaining}")

        send_dietary_options_less_of(user_id)  # Resend updated options if needed

def send_dietary_options_more_of(user_id): # more of function
    """Send updated dietary options to the user based on how many total choices (options + Done)."""
    session = USER_SESSIONS[user_id]
    remaining_options = session["more_of_dietary_preferences"]["remaining"]
    num_choices = len(remaining_options) + 1  # +1 for 'Done'

    if (len(remaining_options) + 1) <= 1:
        # If 1 or fewer real options left, skip and move on
        session["more_of_dietary_preferences"]["in_progress"] = False
        session["awaiting_list"] = True
        send_whatsapp_message(os.getenv("INPUT_LIST"), user_id)
        return

    # Build content variables
    content_variables = {}
    for idx, option in enumerate(remaining_options, start=1):
        content_variables[str(idx * 2 - 1)] = option
        content_variables[str(idx * 2)] = option.lower()

    # Always add Done at the end
    next_index = len(content_variables) + 1
    content_variables[str(next_index)] = "Done"
    content_variables[str(next_index + 1)] = "done"

    content_variables_json = json.dumps(content_variables)

    # Choose template based on TOTAL choices (real options + Done)
    if num_choices == 6:
        template_id = os.getenv("6_dietary_goals_more_of")  # 5 options + Done
    elif num_choices == 5:
        template_id = os.getenv("5_dietary_goals_more_of")  # 4 options + Done
    elif num_choices == 4:
        template_id = os.getenv("4_dietary_goals_more_of")  # 4 options + Done
    elif num_choices == 3:
        template_id = os.getenv("3_dietary_goals_more_of")  # 3 options + Done
    elif num_choices == 2:
        template_id = os.getenv("2_dietary_goals_more_of")  # 2 options + Done
    else:
        template_id = os.getenv("2_dietary_goals_more_of")  # fallback safety

    print(content_variables_json)
    print(f"Template chosen: {template_id}")

    send_whatsapp_message(template_id, user_id, content_variables_json)

def collect_dietary_info_more_of(user_id, user_message):
    """Handle user input during dietary preferences selection."""
    normalized_message = user_message.strip().lower()

    session = USER_SESSIONS[user_id]
    remaining = session["more_of_dietary_preferences"]["remaining"]
    selected = session["more_of_dietary_preferences"]["selected"]

    # FIRST: check if user typed 'done'
    if normalized_message == "done":
        session["more_of_dietary_preferences"]["in_progress"] = False
        session["awaiting_list"] = True
        send_whatsapp_message(os.getenv("INPUT_LIST"), user_id)
        return

    # THEN: check if they picked an available option
    match = None
    for option in remaining:
        if normalized_message == option.lower():
            match = option
            break

    if match:
        selected.append(match)
        remaining.remove(match)

        print(f"User {user_id} selected '{match}'. Remaining options: {remaining}")

        send_dietary_options_more_of(user_id)  # Resend updated options if needed

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


    if normalized_message == "done":
        # Finalize the user's list
        USER_SESSIONS[user_id]["awaiting_list"] = False
        USER_SESSIONS[user_id]["awaiting_options"] = True  # Transition to options state
        user_list = USER_SESSIONS[user_id]["list_items"]

        # Process the list (e.g., save to a database or perform actions)
        print(f"Processing list for user {user_id}: {user_list}")

        # Send a confirmation message and next steps in the flow to view
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


    if normalized_message == "add/remove items":
            # Logic to handle adding/removing items
            # Inform the user about list modification mode
            user_list = USER_SESSIONS[user_id]["list_items"]

            list_string = ", ".join(user_list)  # Join list items nicely
            list_items = {
                "1": list_string 
            }
            list_items = json.dumps(list_items)

            send_whatsapp_message(os.getenv("LIST_MODIFICATION_MODE"), user_id, list_items)
            
            # Switch user back to list building mode
            USER_SESSIONS[user_id]["awaiting_options"] = False
            USER_SESSIONS[user_id]["add_remove_list"] = True

    elif normalized_message == "get recommendations":
        USER_SESSIONS[user_id]["awaiting_options"] = False
        USER_SESSIONS[user_id]["get_recs"] = True

        # Send the message with preferences passed through
        send_whatsapp_message(os.getenv("GET_RECS"), user_id)
       
    elif normalized_message == "manage preferences":
        session = USER_SESSIONS[user_id]

        # Get selected items
        less_of_selected = USER_SESSIONS[user_id]["less_of_dietary_preferences"]["selected"]
        more_of_selected = USER_SESSIONS[user_id]["more_of_dietary_preferences"]["selected"]

        # Format into a user-friendly message
        if less_of_selected:
            less_of_str = ", ".join(less_of_selected)
        else:
            less_of_str = "None selected"

        if more_of_selected:
            more_of_str = ", ".join(more_of_selected)
        else:
            more_of_str = "None selected"

        # Build the content variables (you can format however your template expects)
        content_variables = {
            "1": less_of_str,
            "2": more_of_str
        }

        content_variables_json = json.dumps(content_variables)

        # Send the preferences summary message
        send_whatsapp_message(os.getenv("MANAGE_PREFERENCES_SUMMARY"), user_id, content_variables_json)

        # Reset states or continue as you like
        session["awaiting_options"] = False
        session["awaiting_list"] = False
        session["change_preferences"] = True
        
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

    if normalized_message == "add items":
        # Logic to handle adding/removing items
        # Inform the user about list modification mode
        send_whatsapp_message(os.getenv("ADD_ITEMS"), user_id, list_items)
        
        # Switch user back to list building mode
        USER_SESSIONS[user_id]["add_remove_list"] = False
        USER_SESSIONS[user_id]["add_items"] = True

    elif normalized_message == "remove items":
        
        send_whatsapp_message(os.getenv("REMOVE_ITEMS"), user_id, list_items)
        
        # Switch user back to list building mode
        USER_SESSIONS[user_id]["add_remove_list"] = False
        USER_SESSIONS[user_id]["remove_items"] = True

    elif normalized_message == "nevermind":
        
        # Switch user back to list building mode
        USER_SESSIONS[user_id]["add_remove_list"] = False
        USER_SESSIONS[user_id]["awaiting_options"] = True

        send_whatsapp_message(os.getenv("OPTIONS"), user_id)


def handle_add_items(user_id, user_message):

    normalized_message = user_message.strip().lower().replace("’", "'")  # Replace curly with straight apostrophe

    if normalized_message == "done":
        
        USER_SESSIONS[user_id]["add_items"] = False
        USER_SESSIONS[user_id]["awaiting_options"] = True  # Transition to options state
        user_list = USER_SESSIONS[user_id]["list_items"]

        print(f"Processing list for user {user_id}: {user_list}")

        user_list = USER_SESSIONS[user_id]["list_items"]
   
        list_string = ", ".join(user_list)  # Join the items in the list with commas

        print(f"User {user_id} list: {list_string}")

        list_items = {
            "1": list_string 
        }

        list_items=json.dumps(list_items)

        # Send a confirmation message
        send_whatsapp_message(os.getenv("DONE_LIST"), user_id, list_items)
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

    if normalized_message == "done":
        
        USER_SESSIONS[user_id]["remove_items"] = False
        USER_SESSIONS[user_id]["awaiting_options"] = True  # Transition to options state
        user_list = USER_SESSIONS[user_id]["list_items"]

        print(f"Processing list for user {user_id}: {user_list}")

        user_list = USER_SESSIONS[user_id]["list_items"]
   
        list_string = ", ".join(user_list)  # Join the items in the list with commas

        print(f"User {user_id} list: {list_string}")

        list_items = {
            "1": list_string 
        }

        list_items=json.dumps(list_items)

        # Send a confirmation message
        send_whatsapp_message(os.getenv("DONE_LIST"), user_id, list_items)
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

def change_preferences(user_id, user_message):
    """
    Handle user input after showing preferences summary.
    User can choose to update 'less of', 'more of', or go back.
    """
    normalized_message = user_message.strip().lower()

    session = USER_SESSIONS[user_id]

    if normalized_message == "update less of":
        # Reset less_of to allow new selections
        session["less_of_dietary_preferences"]["remaining"] = ["Sodium", "Saturated Fats", "Added Sugars", "Animal Proteins"]
        session["less_of_dietary_preferences"]["selected"] = []
        session["less_of_dietary_preferences"]["in_progress"] = True
        session["change_preferences"] = False  # Exit change preferences mode

        send_dietary_options_less_of(user_id)

    elif normalized_message == "update more of":
        # Reset more_of to allow new selections
        session["more_of_dietary_preferences"]["remaining"] = ["Fruits", "Vegetables", "Fish", "Whole Grains", "Plant Proteins"]
        session["more_of_dietary_preferences"]["selected"] = []
        session["more_of_dietary_preferences"]["in_progress"] = True
        session["change_preferences"] = False  # Exit change preferences mode

        send_dietary_options_more_of(user_id)

    elif normalized_message == "nevermind":
        # Just send back to options
        session["change_preferences"] = False
        session["awaiting_options"] = True

        send_whatsapp_message(os.getenv("OPTIONS"), user_id)