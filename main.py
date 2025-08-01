# -----------------------------
# file: main.py
# -----------------------------

import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
from odoo_connector import (
    create_odoo_contact,
    update_odoo_contact,
    find_existing_contact,
    create_odoo_opportunity,
    connect_odoo,
    get_or_create_opportunity_tags,
    find_odoo_user_id,
    create_odoo_activity,
    get_model_id,
    find_closest_dealer,
    find_existing_opportunity,
    update_odoo_opportunity,
    ODOO_URL 
)
from datetime import datetime, timedelta
import time
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

print("Script Started")

geolocator = Nominatim(user_agent="WavcorLeadParserApp")

def get_lat_lon_from_address(city, province_state, country="Canada", attempt=1):
    # ... (rest of your get_lat_lon_from_address function - no changes here)
    """
    Geocodes a city and province/state to get its latitude and longitude.
    Includes basic retry logic.
    """
    full_address = f"{city}, {province_state}, {country}"
    print(f"DEBUG: Attempting to geocode: {full_address} (Attempt {attempt})")
    try:
        location = geolocator.geocode(full_address, timeout=10)
        if location:
            print(f"DEBUG: Geocoded successfully. Lat: {location.latitude}, Lon: {location.longitude}")
            return location.latitude, location.longitude
        else:
            print(f"WARNING: Could not geocode '{full_address}'. Location not found.")
            return None, None
    except GeocoderTimedOut:
        print(f"WARNING: Geocoding service timed out for '{full_address}'. Retrying in 2 seconds...")
        time.sleep(2)
        if attempt < 3:
            return get_lat_lon_from_address(city, province_state, country, attempt + 1)
        else:
            print(f"ERROR: Geocoding timed out after multiple attempts for '{full_address}'.")
            return None, None
    except GeocoderServiceError as e:
        print(f"ERROR: Geocoding service error for '{full_address}': {e}")
        return None, None
    except Exception as e:
        print(f"ERROR: An unexpected error occurred during geocoding for '{full_address}': {e}")
        return None, None

def display_clickable_link(url, label="Opportunity URL:"):
    """
    Inserts a clickable and copyable URL into the result_output Text widget.
    """
    # Ensure result_output is accessible (it's a global variable in your current setup)
    global result_output 

    result_output.insert(tk.END, f"\n{label} ", "bold_label") # Add label
    
    # Get the current position for the start of the link
    start_index = result_output.index(tk.END + "-1c linestart") 
    result_output.insert(tk.END, url, "link") # Insert the URL with a special 'link' tag
    
    # Get the current position for the end of the link
    end_index = result_output.index(tk.END + "-1c") 

    # Configure the 'link' tag for appearance (blue, underline)
    result_output.tag_config("link", foreground="blue", underline=True)
    # Configure a 'bold_label' tag for the label for better readability
    result_output.tag_config("bold_label", font=("Arial", 10, "bold"))
    
    # Bind the left-click event to the 'link' tag
    # When clicked, it will open the URL in the default web browser
    result_output.tag_bind("link", "<Button-1>", lambda event, link_url=url: webbrowser.open(link_url))
    
    # Optional: Change cursor to a hand when hovering over the link
    result_output.tag_bind("link", "<Enter>", lambda event: result_output.config(cursor="hand2"))
    result_output.tag_bind("link", "<Leave>", lambda event: result_output.config(cursor="arrow"))

    result_output.insert(tk.END, "\n") # Add a newline after the link for neatness
    result_output.see(tk.END) # Scroll to the end to make the new link visible


def extract_data():
    text = input_text.get("1.0", tk.END)
    lines = text.splitlines()

    # --- CRITICAL DEBUG PRINT: Show all input lines as seen by the script ---
    print("\n--- DEBUG: Raw input lines (start) ---")
    for idx, line_val in enumerate(lines):
        # Using repr() to show invisible characters like spaces, tabs, newlines if any
        print(f"Line {idx}: '{repr(line_val)}'") 
    print("--- DEBUG: Raw input lines (end) ---\n")
    # --- END CRITICAL DEBUG PRINT ---

    data = {
        "Name": "",
        "Email": "",
        "Phone": "",
        "City": "",
        "Prov/State": "",
        "Products Interest": [],
        "Message": ""
    }

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        print(f"DEBUG: Main loop - Processing line {i}: '{line}'") # Added for general loop visibility

        if line.startswith("Name:"):
            data["Name"] = line.replace("Name:", "").strip()
        elif line.startswith("Email:"):
            data["Email"] = line.replace("Email:", "").strip()
        elif line.startswith("Phone:"):
            data["Phone"] = line.replace("Phone:", "").strip()
        elif line.startswith("City:"):
            data["City"] = line.replace("City:", "").strip()
        elif line.startswith("Prov/State:"):
            data["Prov/State"] = line.replace("Prov/State:", "").strip()
        elif line.startswith("Products Interest:"):
            products_text = line.replace("Products Interest:", "").strip()
            i += 1
            while i < len(lines) and not any(lines[i].startswith(prefix) for prefix in ["Message:", "Name:", "Email:", "Phone:", "City:", "Prov/State:", "Products Interest:"]):
                products_text += " " + lines[i].strip()
                i += 1
            i -= 1
            data["Products Interest"] = [p.strip() for p in products_text.split(",") if p.strip()]
        # --- REVISED MESSAGE PARSING LOGIC (THIS IS THE ONE YOU NEED) ---
        elif line.startswith("Message:"):
            print(f"DEBUG: --- Message parsing started at line index {i} ---")
            print(f"DEBUG: Current line (stripped): '{line}'")

            # Extract content directly from the "Message:" line itself
            message_content_parts = [line.replace("Message:", "", 1).strip()] # <-- THIS IS THE CRITICAL CHANGE

            current_line_index = i + 1 # Move to the next line to check for multi-line content

            print(f"DEBUG: Initial current_line_index for multi-line message content: {current_line_index}")
            print(f"DEBUG: Initial content from 'Message:' line: '{message_content_parts[0]}'") # <-- THIS DEBUG PRINT CONFIRMS FIRST PART
            print(f"DEBUG: Total lines available: {len(lines)}")

            # Collect any subsequent lines that are not new fields
            # This loop implicitly handles blank lines by checking if a line starts a new field.
            while current_line_index < len(lines) and \
                  not any(lines[current_line_index].strip().startswith(prefix) 
                          for prefix in ["Name:", "Email:", "Phone:", "City:", "Prov/State:", "Products Interest:"]):
                
                # Add the stripped line to parts, unless it's just an empty line
                stripped_sub_line = lines[current_line_index].strip()
                if stripped_sub_line: # Only add if not an empty string after stripping
                    message_content_parts.append(stripped_sub_line)
                    print(f"DEBUG: Collecting multi-line message part at index {current_line_index}: '{repr(lines[current_line_index])}' (stripped: '{stripped_sub_line}')")
                else:
                    print(f"DEBUG: Skipping empty multi-line message part at index {current_line_index}: '{repr(lines[current_line_index])}'")

                current_line_index += 1
            
            data["Message"] = "\n".join(part for part in message_content_parts if part).strip() # Join only non-empty parts
            
            print(f"DEBUG: Parsed Message (final result): '{data['Message']}'")
            print(f"DEBUG: --- Message parsing ended ---")
            
            # Since "Message:" is typically the last field, we'll break the main loop here.
            # If there could be other fields *after* Message:, you would remove this break.
            break 
        # --- END REVISED MESSAGE PARSING LOGIC ---
        i += 1 # Move to the next line in the main loop (only if break wasn't called)

    result_output.delete("1.0", tk.END)
    for key, value in data.items():
        if isinstance(value, list):
            value = ", ".join(value)
        result_output.insert(tk.END, f"{key}: {value}\n")

    contact_id = None

    # Push to Odoo with confirmation
    existing = find_existing_contact(data)
    if existing:
        decision = messagebox.askyesno(
            "Contact Exists",
            f"Contact '{existing['name']}' already exists.\nDo you want to update this contact?"
        )
        if decision:
            success = update_odoo_contact(existing['id'], data)
            if success:
                messagebox.showinfo("Updated", "Contact updated in Odoo.")
                contact_id = existing['id']
            else:
                messagebox.showerror("Update Failed", "Failed to update contact in Odoo.")
        else:
            messagebox.showinfo("Skipped", "No changes were made to the existing contact.")
            contact_id = existing['id']
    else:
        decision = messagebox.askyesno(
            "Create New Contact",
            f"No existing contact found.\nDo you want to create a new contact for '{data['Name']}'?"
        )
        if decision:
            new_id = create_odoo_contact(data)
            if new_id:
                messagebox.showinfo("Created", f"New contact created with ID {new_id}.")
                contact_id = new_id
            else:
                messagebox.showerror("Error", "Failed to create new contact.")
        else:
            messagebox.showinfo("Cancelled", "Contact was not created.")

    # --- Opportunity Creation/Update Logic ---
    if contact_id:
        opportunity_name = data['Name'] # Opportunity name directly matches contact name

        # First, check if an opportunity with this name already exists
        existing_opportunity = find_existing_opportunity(opportunity_name)
        
        opportunity_id = None # To store the ID of the opportunity (new or existing)
        opportunity_url = "" # To store the URL

        if existing_opportunity:
            update_opportunity_decision = messagebox.askyesno(
                "Opportunity Exists",
                f"An opportunity named '{opportunity_name}' already exists (ID: {existing_opportunity['id']}).\nDo you want to update this existing opportunity?"
            )
            if update_opportunity_decision:
                uid, models = connect_odoo()
                if not uid:
                    messagebox.showerror("Connection Error", "Failed to connect to Odoo for opportunity update.")
                    return

                print(f"DEBUG: Updating existing opportunity ID: {existing_opportunity['id']}")
                opportunity_tag_ids = get_or_create_opportunity_tags(models, uid, data['Products Interest'])
                
                update_opportunity_data = {
                    'partner_id': contact_id, # Ensure partner is linked
                    'description': data['Message'],
                    'tag_ids': [(6, 0, opportunity_tag_ids)] if opportunity_tag_ids else False
                }
                print(f"DEBUG: Attempting to update opportunity with data: {update_opportunity_data}")
                success = update_odoo_opportunity(existing_opportunity['id'], update_opportunity_data)
                if success:
                    opportunity_id = existing_opportunity['id']
                    opportunity_url = f"{ODOO_URL}/web#id={opportunity_id}&model=crm.lead" # Construct URL
                    #messagebox.showinfo("Opportunity Updated", f"Opportunity '{opportunity_name}' updated in Odoo.\n\nURL: {opportunity_url}")
                    messagebox.showinfo("Opportunity Updated", f"Opportunity '{opportunity_name}' updated in Odoo.")
                    display_clickable_link(opportunity_url) # Display the link in result_output
                else:
                    messagebox.showerror("Opportunity Update Error", "Failed to update existing opportunity.")
            else:
                messagebox.showinfo("Opportunity Skipped", "Existing opportunity was not updated.")
                opportunity_id = existing_opportunity['id'] # Still use its ID for activity/dealer
                opportunity_url = f"{ODOO_URL}/web#id={opportunity_id}&model=crm.lead" # Construct URL for skipped update
        else:
            # No existing opportunity, ask to create a new one
            create_opportunity_decision = messagebox.askyesno(
                "Create New Opportunity",
                f"No existing opportunity found with name '{opportunity_name}'.\nDo you want to create a new one?"
            )
            if create_opportunity_decision:
                uid, models = connect_odoo()
                if not uid:
                    messagebox.showerror("Connection Error", "Failed to connect to Odoo for opportunity creation.")
                    return

                print(f"DEBUG: Creating new opportunity: {opportunity_name}")
                opportunity_tag_ids = get_or_create_opportunity_tags(models, uid, data['Products Interest'])

                opportunity_data_for_create = {
                    'name': opportunity_name,
                    'partner_id': contact_id,
                    'description': data['Message'],
                    'tag_ids': [(6, 0, opportunity_tag_ids)] if opportunity_tag_ids else False
                }
                print(f"DEBUG: Attempting to create opportunity with data: {opportunity_data_for_create}")
                new_id = create_odoo_opportunity(opportunity_data_for_create)
                if new_id:
                    opportunity_id = new_id
                    opportunity_url = f"{ODOO_URL}/web#id={opportunity_id}&model=crm.lead" # Construct URL
                    #messagebox.showinfo("Opportunity Created", f"New opportunity created with ID {new_id}.\n\nURL: {opportunity_url}")
                    messagebox.showinfo("Opportunity Created", f"New opportunity created with ID {new_id}.")
                    display_clickable_link(opportunity_url) # Display the link in result_output
                
                else:
                    messagebox.showerror("Opportunity Error", "Failed to create new opportunity.")
            else:
                messagebox.showinfo("Opportunity Skipped", "Opportunity was not created.")

        # --- Activity and Dealer Recommendation (only if an opportunity ID is available) ---
        if opportunity_id:
            # Create Follow-Up Activity
            print("DEBUG: Attempting to create follow-up activity...")
            # Note: models and uid are from the last successful connect_odoo call, usually from creating/updating the opportunity
            # If for some reason uid/models are stale here, you might need to call connect_odoo() again.
            # For this context, it's generally fine as it runs immediately after opportunity interaction.
            hal_pepler_user_id = find_odoo_user_id(models, uid, "Hal Pepler")
            
            if hal_pepler_user_id:
                activity_date = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
                print(f"DEBUG: Activity deadline date: {activity_date}")
                
                crm_lead_model_id = get_model_id(models, uid, 'crm.lead') 

                if crm_lead_model_id:
                    activity_data = {
                        'res_model_id': crm_lead_model_id,
                        'res_id': opportunity_id,
                        'user_id': hal_pepler_user_id,
                        'summary': 'Follow up on email',
                        'date_deadline': activity_date,
                        'note': f"Follow-up for opportunity '{opportunity_name}'. URL: {opportunity_url}" # Added URL to activity note
                    }
                    print(f"DEBUG: Activity data: {activity_data}")
                    activity_created = create_odoo_activity(models, uid, activity_data)
                    if activity_created:
                        messagebox.showinfo("Activity Created", f"Follow-up activity created for Opportunity ID {opportunity_id}.")
                    else:
                        messagebox.showerror("Activity Error", "Failed to create follow-up activity.")
                else:
                    messagebox.showwarning("Activity Skipped", "Could not get Odoo model ID for 'crm.lead'. Activity not created.")
            else:
                messagebox.showwarning("Activity Skipped", "Could not find 'Hal Pepler' in Odoo. Activity not created.")
            # --- End Follow-Up Activity ---

            # --- Find and Recommend Closest Dealer ---
            print("DEBUG: Attempting to find closest dealer...")
            customer_lat, customer_lon = None, None

            if data['City'] and data['Prov/State']:
                customer_lat, customer_lon = get_lat_lon_from_address(data['City'], data['Prov/State'])
            else:
                messagebox.showwarning("Geocoding Skipped", "Customer City or Province/State missing. Cannot geocode for dealer recommendation.")

            if customer_lat is not None and customer_lon is not None:
                closest_dealer = find_closest_dealer(customer_lat, customer_lon)

                if closest_dealer:
                    dealer_info = (f"Closest Dealer: {closest_dealer['Location']}\n"
                                   f"Contact: {closest_dealer['Contact']}\n"
                                   f"Phone: {closest_dealer['Phone']}\n"
                                   f"Distance: {closest_dealer['Distance_km']} km")
                    result_output.insert(tk.END, "\n--- Closest Dealer Recommendation ---\n", "bold_label")
                    result_output.insert(tk.END, dealer_info + "\n")
                    result_output.insert(tk.END, "-------------------------------------\n\n", "bold_label")
                    result_output.see(tk.END) # Scroll to the end to show the new information
                    
                else:
                    messagebox.showwarning("Dealer Recommendation", "Could not find any dealer locations or calculate closest.")
            else:
                messagebox.showwarning("Dealer Recommendation Skipped", "Could not determine customer's coordinates. Dealer recommendation skipped.")
            # --- End Find and Recommend Closest Dealer ---

        else:
            messagebox.showinfo("Opportunity Related Actions Skipped", "No opportunity was created or identified, so no activity or dealer recommendation was made.")
    else:
        messagebox.showinfo("Opportunity Skipped", "No contact was created or identified, so no opportunity was created.")

root = tk.Tk()
root.title("Odoo Lead Parser")

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

ttk.Label(frame, text="Paste Odoo CRM Text:").grid(row=0, column=0, sticky=tk.W)

# --- MODIFIED: input_text widget ---
input_text = tk.Text(frame, width=80, height=12,
                     bg="white",    # Explicit background color
                     fg="black",    # Explicit foreground (text) color
                     font=("Arial", 10)) # Explicit font and size
input_text.grid(row=1, column=0, padx=5, pady=5)

ttk.Button(frame, text="Extract & Sync to Odoo", command=extract_data).grid(row=2, column=0, pady=5)

ttk.Label(frame, text="Extracted Output:").grid(row=3, column=0, sticky=tk.W)

# --- MODIFIED: result_output widget ---
result_output = tk.Text(frame, width=80, height=12,
                        background="#f0f0f0", # Your existing background color
                        fg="black",           # Explicit foreground (text) color
                        font=("Arial", 10))   # Explicit font and size
result_output.grid(row=4, column=0, padx=5, pady=5)

root.mainloop()