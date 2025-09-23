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
    post_internal_note_to_opportunity, # Ensure this is imported if you added it previously
    ODOO_URL, 
    normalize_state
)
from datetime import datetime, timedelta
import time
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

print("Script Started")

geolocator = Nominatim(user_agent="WavcorLeadParserApp")

def get_lat_lon_from_address(city, province_state, country="Canada", attempt=1):
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

    data = {
        "Name": "", "Email": "", "Phone": "", "City": "", "Prov/State": "",
        "Products Interest": [], "Message": ""
    }

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("Name:"):
            data["Name"] = line.replace("Name:", "").strip()
        elif line.startswith("Email:"):
            data["Email"] = line.replace("Email:", "").strip()
        elif line.startswith("Phone:"):
            data["Phone"] = line.replace("Phone:", "").strip()
        elif line.startswith("City:"):
            data["City"] = line.replace("City:", "").strip()
        elif line.startswith("Prov/State:"):
            raw_state = line.replace("Prov/State:", "").strip()
            data["Prov/State"] = normalize_state(raw_state)
        elif line.startswith("Products Interest:"):
            products_text = line.replace("Products Interest:", "").strip()
            i += 1
            while i < len(lines) and not any(lines[i].strip().startswith(prefix) for prefix in ["Message:", "Name:", "Email:", "Phone:", "City:", "Prov/State:", "Products Interest:"]):
                products_text += " " + lines[i].strip()
                i += 1
            i -= 1
            data["Products Interest"] = [p.strip() for p in products_text.split(",") if p.strip()]
        elif line.startswith("Message:"):
            message_content_parts = [line.replace("Message:", "", 1).strip()]
            current_line_index = i + 1
            while current_line_index < len(lines) and not any(lines[current_line_index].strip().startswith(prefix) for prefix in ["Name:", "Email:", "Phone:", "City:", "Prov/State:", "Products Interest:"]):
                stripped_sub_line = lines[current_line_index].strip()
                if stripped_sub_line:
                    message_content_parts.append(stripped_sub_line)
                current_line_index += 1
            data["Message"] = "\n".join(part for part in message_content_parts if part).strip()
            break
        i += 1

    result_output.delete("1.0", tk.END)
    for key, value in data.items():
        if isinstance(value, list):
            value = ", ".join(value)
        result_output.insert(tk.END, f"{key}: {value}\n")

    # --- Find and Recommend Closest Dealer and append to Message ---
    print("DEBUG: Attempting to find closest dealer...")
    dealer_info_for_append = ""
    customer_lat, customer_lon = None, None
    if data['City'] and data['Prov/State']:
        customer_lat, customer_lon = get_lat_lon_from_address(data['City'], data['Prov/State'])
    else:
        print("WARNING: Customer City or Province/State missing. Cannot geocode for dealer recommendation.")

    if customer_lat is not None and customer_lon is not None:
        closest_dealer = find_closest_dealer(customer_lat, customer_lon)
        if closest_dealer:
            dealer_info_for_append = (f"Closest Dealer: {closest_dealer['Location']}\n"
                                      f"Contact: {closest_dealer['Contact']}\n"
                                      f"Phone: {closest_dealer['Phone']}\n"
                                      f"Distance: {closest_dealer['Distance_km']} km")
            
            # Display dealer info in the GUI
            result_output.insert(tk.END, "\n--- Closest Dealer Recommendation ---\n", "bold_label")
            result_output.insert(tk.END, dealer_info_for_append + "\n")
            result_output.insert(tk.END, "-------------------------------------\n\n", "bold_label")
            result_output.see(tk.END)
    else:
        print("WARNING: Could not determine customer's coordinates. Dealer recommendation skipped.")

    # Combine original message with dealer info for Odoo's 'description' field
    combined_message = data['Message']
    if dealer_info_for_append:
        combined_message += "\n\n--- Closest Dealer Recommendation ---\n" + dealer_info_for_append
    
    # Convert all newline characters to HTML <br> tags for Odoo to render them correctly
    combined_message_for_odoo = combined_message.replace('\n', '<br>')

    # --- Odoo Sync Logic ---
    contact_id = None
    existing = find_existing_contact(data)
    if existing:
        decision = messagebox.askyesno("Contact Exists", f"Contact '{existing['name']}' already exists.\nDo you want to update this contact?")
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
        decision = messagebox.askyesno("Create New Contact", f"No existing contact found.\nDo you want to create a new contact for '{data['Name']}'?")
        if decision:
            new_id = create_odoo_contact(data)
            if new_id:
                messagebox.showinfo("Created", f"New contact created with ID {new_id}.")
                contact_id = new_id
            else:
                messagebox.showerror("Error", "Failed to create new contact.")
        else:
            messagebox.showinfo("Cancelled", "Contact was not created.")

    if contact_id:
        opportunity_name = data['Name']
        existing_opportunity = find_existing_opportunity(opportunity_name)
        opportunity_id = None
        opportunity_url = ""

        uid, models = connect_odoo()
        if not uid:
            messagebox.showerror("Connection Error", "Failed to connect to Odoo for opportunity actions.")
            return

        opportunity_tag_ids = get_or_create_opportunity_tags(models, uid, data['Products Interest'])
        
        if existing_opportunity:
            update_opportunity_decision = messagebox.askyesno("Opportunity Exists", f"An opportunity named '{opportunity_name}' already exists (ID: {existing_opportunity['id']}).\nDo you want to update this existing opportunity?")
            if update_opportunity_decision:
                update_opportunity_data = {
                    'partner_id': contact_id,
                    'description': combined_message_for_odoo,
                    'tag_ids': [(6, 0, opportunity_tag_ids)] if opportunity_tag_ids else False
                }
                success = update_odoo_opportunity(existing_opportunity['id'], update_opportunity_data)
                if success:
                    opportunity_id = existing_opportunity['id']
                    opportunity_url = f"{ODOO_URL}/web#id={opportunity_id}&model=crm.lead"
                    #messagebox.showinfo("Opportunity Updated", f"Opportunity '{opportunity_name}' updated in Odoo.")
                    display_clickable_link(opportunity_url)
                else:
                    messagebox.showerror("Opportunity Update Error", "Failed to update existing opportunity.")
            else:
                #messagebox.showinfo("Opportunity Skipped", "Existing opportunity was not updated.")
                opportunity_id = existing_opportunity['id']
                opportunity_url = f"{ODOO_URL}/web#id={opportunity_id}&model=crm.lead"
        else:
            create_opportunity_decision = messagebox.askyesno("Create New Opportunity", f"No existing opportunity found with name '{opportunity_name}'.\nDo you want to create a new one?")
            if create_opportunity_decision:
                opportunity_data_for_create = {
                    'name': opportunity_name,
                    'partner_id': contact_id,
                    'description': combined_message_for_odoo,
                    'tag_ids': [(6, 0, opportunity_tag_ids)] if opportunity_tag_ids else False
                }
                new_id = create_odoo_opportunity(opportunity_data_for_create)
                if new_id:
                    opportunity_id = new_id
                    opportunity_url = f"{ODOO_URL}/web#id={opportunity_id}&model=crm.lead"
                    #messagebox.showinfo("Opportunity Created", f"New opportunity created with ID {new_id}.")
                    display_clickable_link(opportunity_url)
                else:
                    messagebox.showerror("Opportunity Error", "Failed to create new opportunity.")
            #else:
                #messagebox.showinfo("Opportunity Skipped", "Opportunity was not created.")

        if opportunity_id:
            create_activity_decision = messagebox.askyesno("Create Follow-Up Activity", f"Do you want to create a follow-up activity for opportunity '{opportunity_name}'?")
            if create_activity_decision:
                hal_pepler_user_id = find_odoo_user_id(models, uid, "Hal Pepler")
                if hal_pepler_user_id:
                    activity_date = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
                    crm_lead_model_id = get_model_id(models, uid, 'crm.lead')
                    if crm_lead_model_id:
                        activity_data = {
                            'res_model_id': crm_lead_model_id, 'res_id': opportunity_id,
                            'user_id': hal_pepler_user_id, 'summary': 'Follow up on email',
                            'date_deadline': activity_date, 'note': f"Follow-up for opportunity '{opportunity_name}'. URL: {opportunity_url}"
                        }
                        activity_created = create_odoo_activity(models, uid, activity_data)
                        if not activity_created:
                            #messagebox.showinfo("Activity Created", f"Follow-up activity created for Opportunity ID {opportunity_id}.")
                        #else:
                            messagebox.showerror("Activity Error", "Failed to create follow-up activity.")
                    #else:
                        #messagebox.showwarning("Activity Skipped", "Could not get Odoo model ID for 'crm.lead'. Activity not created.")
                else:
                    messagebox.showwarning("Activity Skipped", "Could not find 'Hal Pepler' in Odoo. Activity not created.")
            #else:
                #messagebox.showinfo("Activity Skipped", "Follow-up activity was not created per user's choice.")

root = tk.Tk()
root.title("Odoo Lead Parser version 004")

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

ttk.Label(frame, text="Paste Odoo CRM Text:").grid(row=0, column=0, sticky=tk.W)

input_text = tk.Text(frame, width=80, height=12,
                     bg="white",    # Explicit background color
                     fg="black",    # Explicit foreground (text) color
                     font=("Arial", 10)) # Explicit font and size
input_text.grid(row=1, column=0, padx=5, pady=5)

ttk.Button(frame, text="Extract & Sync to Odoo", command=extract_data).grid(row=2, column=0, pady=5)

ttk.Label(frame, text="Extracted Output:").grid(row=3, column=0, sticky=tk.W)

result_output = tk.Text(frame, width=80, height=12,
                         background="#f0f0f0", # Your existing background color
                         fg="black",           # Explicit foreground (text) color
                         font=("Arial", 10))   # Explicit font and size
result_output.grid(row=4, column=0, padx=5, pady=5)

root.mainloop()