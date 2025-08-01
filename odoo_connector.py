# -----------------------------
# file: odoo_connector.py
# -----------------------------
import xmlrpc.client
from datetime import datetime, timedelta 
import math

ODOO_URL = 'https://wavcor-international-inc2.odoo.com'
#ODOO_URL = 'https://wavcor-test-2025-07-20.odoo.com'
ODOO_DB = 'wavcor-international-inc2'
#ODOO_DB = 'wavcor-test-2025-07-20'
ODOO_USERNAME = 'jason@wavcor.ca'
ODOO_PASSWORD = 'Wavcor3702?'

def connect_odoo():
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
    return uid, models

STATE_TO_COUNTRY_MAP = {
    # Canadian Provinces and Territories
    'AB': 'Canada', 'Alberta': 'Canada',
    'BC': 'Canada', 'British Columbia': 'Canada',
    'MB': 'Canada', 'Manitoba': 'Canada',
    'NB': 'Canada', 'New Brunswick': 'Canada',
    'NL': 'Canada', 'Newfoundland and Labrador': 'Canada',
    'NS': 'Canada', 'Nova Scotia': 'Canada',
    'ON': 'Canada', 'Ontario': 'Canada',
    'PE': 'Canada', 'Prince Edward Island': 'Canada',
    'QC': 'Canada', 'Quebec': 'Canada',
    'SK': 'Canada', 'Saskatchewan': 'Canada',
    'NT': 'Canada', 'Northwest Territories': 'Canada',
    'NU': 'Canada', 'Nunavut': 'Canada',
    'YT': 'Canada', 'Yukon': 'Canada',

    # US States
    'AL': 'United States', 'Alabama': 'United States',
    'AK': 'United States', 'Alaska': 'United States',
    'AZ': 'United States', 'Arizona': 'United States',
    'AR': 'United States', 'Arkansas': 'United States',
    'CA': 'United States', 'California': 'United States',
    'CO': 'United States', 'Colorado': 'United States',
    'CT': 'United States', 'Connecticut': 'United States',
    'DE': 'United States', 'Delaware': 'United States',
    'FL': 'United States', 'Florida': 'United States',
    'GA': 'United States', 'Georgia': 'United States',
    'HI': 'United States', 'Hawaii': 'United States',
    'ID': 'United States', 'Idaho': 'United States',
    'IL': 'United States', 'Illinois': 'United States',
    'IN': 'United States', 'Indiana': 'United States',
    'IA': 'United States', 'Iowa': 'United States',
    'KS': 'United States', 'Kansas': 'United States',
    'KY': 'United States', 'Kentucky': 'United States',
    'LA': 'United States', 'Louisiana': 'United States',
    'ME': 'United States', 'Maine': 'United States',
    'MD': 'United States', 'Maryland': 'United States',
    'MA': 'United States', 'Massachusetts': 'United States',
    'MI': 'United States', 'Michigan': 'United States',
    'MN': 'United States', 'Minnesota': 'United States',
    'MS': 'United States', 'Mississippi': 'United States',
    'MO': 'United States', 'Missouri': 'United States',
    'MT': 'United States', 'Montana': 'United States',
    'NE': 'United States', 'Nebraska': 'United States',
    'NV': 'United States', 'Nevada': 'United States',
    'NH': 'United States', 'New Hampshire': 'United States',
    'NJ': 'United States', 'New Jersey': 'United States',
    'NM': 'United States', 'New Mexico': 'United States',
    'NY': 'United States', 'New York': 'United States',
    'NC': 'United States', 'North Carolina': 'United States',
    'ND': 'United States', 'North Dakota': 'United States',
    'OH': 'United States', 'Ohio': 'United States',
    'OK': 'United States', 'Oklahoma': 'United States',
    'OR': 'United States', 'Oregon': 'United States',
    'PA': 'United States', 'Pennsylvania': 'United States',
    'RI': 'United States', 'Rhode Island': 'United States',
    'SC': 'United States', 'South Carolina': 'United States',
    'SD': 'United States', 'South Dakota': 'United States',
    'TN': 'United States', 'Tennessee': 'United States',
    'TX': 'United States', 'Texas': 'United States',
    'UT': 'United States', 'Utah': 'United States',
    'VT': 'United States', 'Vermont': 'United States',
    'VA': 'United States', 'Virginia': 'United States',
    'WA': 'United States', 'Washington': 'United States',
    'WV': 'United States', 'West Virginia': 'United States',
    'WI': 'United States', 'Wisconsin': 'United States',
    'WY': 'United States', 'Wyoming': 'United States',
    'DC': 'United States', 'District of Columbia': 'United States', # Not a state, but often included

    # Australian States and Territories
    'NSW': 'Australia', 'New South Wales': 'Australia',
    'VIC': 'Australia', 'Victoria': 'Australia',
    'QLD': 'Australia', 'Queensland': 'Australia',
    'SA': 'Australia', 'South Australia': 'Australia',
    'WA': 'Australia', 'Western Australia': 'Australia',
    'TAS': 'Australia', 'Tasmania': 'Australia',
    'ACT': 'Australia', 'Australian Capital Territory': 'Australia',
    'NT': 'Australia', 'Northern Territory': 'Australia',
}

DEALER_LOCATIONS = [
    {"Location": "Mariapolis Agro Centre", "Latitude": 49.360666, "Longitude": -98.98952, "Contact": "Scott Hainsworth", "Phone": "204-723-0249"},
    {"Location": "Baldur Agro Centre", "Latitude": 49.385578, "Longitude": -99.24384, "Contact": "Scott Hainsworth", "Phone": "204-723-0249"},
    {"Location": "Glenboro Agro Centre", "Latitude": 49.555833, "Longitude": -99.291111, "Contact": "Scott Hainsworth", "Phone": "204-723-0249"},
    {"Location": "Minto Agro Centre", "Latitude": 49.4312, "Longitude": -100.2227, "Contact": "Scott Hainsworth", "Phone": "204-723-0249"},
    {"Location": "Manitou Agro Centre", "Latitude": 49.240555, "Longitude": -98.536667, "Contact": "Scott Hainsworth", "Phone": "204-723-0249"},
    {"Location": "Kyle Agro Centre", "Latitude": 50.8327023, "Longitude": -108.0392125, "Contact": "Zane Banadyga", "Phone": "306-750-6603"},
    {"Location": "Frontier Agro Centre", "Latitude": 49.204894, "Longitude": -108.561809, "Contact": "Zane Banadyga", "Phone": "306-750-6603"},
    {"Location": "Maple Creek Agro Centre", "Latitude": 49.8, "Longitude": -109.1, "Contact": "Zane Banadyga", "Phone": "306-750-6603"},
    {"Location": "Gull Lake Agro Centre & Gas Bar", "Latitude": 50.1, "Longitude": -108.4, "Contact": "Zane Banadyga", "Phone": "306-750-6603"},
    {"Location": "Cabri Agro Centre", "Latitude": 50.62, "Longitude": -108.46, "Contact": "Zane Banadyga", "Phone": "306-750-6603"},
    {"Location": "Herbert Farm Centre & Gas Bar", "Latitude": 50.4275233, "Longitude": -107.2234377, "Contact": "Zane Banadyga", "Phone": "306-750-6603"},
    {"Location": "Morse Farm Centre", "Latitude": 50.33425, "Longitude": -106.9663, "Contact": "Zane Banadyga", "Phone": "306-750-6603"},
    {"Location": "Sceptre Farm Centre", "Latitude": 50.86281, "Longitude": -109.27075, "Contact": "Zane Banadyga", "Phone": "306-750-6603"},
    {"Location": "Ponteix Farm Centre", "Latitude": 49.74138, "Longitude": -107.469433, "Contact": "Zane Banadyga", "Phone": "306-750-6603"},
    {"Location": "Swift Current Agro", "Latitude": 50.285765, "Longitude": -107.851187, "Contact": "Zane Banadyga", "Phone": "306-750-6603"},
    {"Location": "Shaunavon Home & Agro Centre", "Latitude": 49.644498, "Longitude": -108.415893, "Contact": "Zane Banadyga", "Phone": "306-750-6603"},
    {"Location": "Eastend Agro Centre", "Latitude": 49.51, "Longitude": -108.82, "Contact": "Zane Banadyga", "Phone": "306-750-6603"},
    {"Location": "Hazlet Agro Centre", "Latitude": 50.4000622, "Longitude": -108.5939493, "Contact": "Zane Banadyga", "Phone": "306-750-6603"},
    {"Location": "Consul Agro Centre & Food Store", "Latitude": 49.2953781, "Longitude": -109.5201135, "Contact": "Zane Banadyga", "Phone": "306-750-6603"},
    {"Location": "Tompkins Farm Centre", "Latitude": 50.067518, "Longitude": -108.805208, "Contact": "Zane Banadyga", "Phone": "306-750-6603"},
    {"Location": "Abbey Farm Centre", "Latitude": 50.7369, "Longitude": -108.7575, "Contact": "Zane Banadyga", "Phone": "306-750-6603"},
    {"Location": "Wiseton Farm Supply", "Latitude": 51.315073, "Longitude": -107.650071, "Contact": "Tony Britnell", "Phone": "306-867-7672"},
    {"Location": "Beechy Farm Supply", "Latitude": 50.8793278, "Longitude": -107.3838575, "Contact": "Tony Britnell", "Phone": "306-867-7672"},
    {"Location": "Outlook Home & Agro", "Latitude": 51.48866, "Longitude": -107.05039, "Contact": "Tony Britnell", "Phone": "306-867-7672"},
    {"Location": "Davidson Home Agro & Liquor", "Latitude": 51.2628546, "Longitude": -105.9890338, "Contact": "Tony Britnell", "Phone": "306-867-7672"},
    {"Location": "Broderick Agro Centre", "Latitude": 51.592881, "Longitude": -106.9175, "Contact": "Tony Britnell", "Phone": "306-867-7672"},
    {"Location": "Strongfield Agro Centre", "Latitude": 51.33159, "Longitude": -106.58952, "Contact": "Tony Britnell", "Phone": "306-867-7672"},
    {"Location": "Tullis Agro Centre", "Latitude": 51.038626, "Longitude": -107.037085, "Contact": "Tony Britnell", "Phone": "306-867-7672"},
    {"Location": "Saskatoon Coop", "Latitude": 52.1332, "Longitude": -106.67, "Contact": "Volodymyr Vakula", "Phone": "306-917-8778"},
    {"Location": "Hepburn Ag Centre", "Latitude": 52.524511, "Longitude": -106.731207, "Contact": "Volodymyr Vakula", "Phone": "306-917-8778"},
    {"Location": "Colonsay Ag Centre", "Latitude": 51.980557, "Longitude": -105.86921, "Contact": "Volodymyr Vakula", "Phone": "306-917-8778"},
    {"Location": "Watrous Ag Centre", "Latitude": 51.676963, "Longitude": -105.483289, "Contact": "Volodymyr Vakula", "Phone": "306-917-8778"},
    {"Location": "Norquay Coop", "Latitude": 51.9833, "Longitude": -102.35, "Contact": "Gerald Fehr", "Phone": "306-594-2215"},
    {"Location": "Wynyard Coop", "Latitude": 51.7833, "Longitude": -104.1667, "Contact": "Victor Hawryluk", "Phone": "306-874-7816"},
    {"Location": "Turtleford", "Latitude": 53.034, "Longitude": -108.973, "Contact": "Kelly Svoboda", "Phone": "306-845-2183"},
    {"Location": "Maidstone Coop", "Latitude": 53.081224, "Longitude": -109.2957338, "Contact": "Kelly Svoboda", "Phone": "306-845-2183"},
]

def get_state_id(models, uid, state_name):
    if not state_name:
        return False
    states = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
        'res.country.state', 'search_read',
        [[('name', 'ilike', state_name.strip())]], {'fields': ['id'], 'limit': 1})
    return states[0]['id'] if states else False

def get_country_id(models, uid, country_name):
    if not country_name:
        return False
    try:
        country = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
            'res.country', 'search_read',
            [[('name', '=', country_name.strip())]], {'fields': ['id'], 'limit': 1})
        return country[0]['id'] if country else False
    except xmlrpc.client.Fault as e:
        print(f"Odoo RPC Error getting country ID for '{country_name}': {e.faultString}")
        return False
    except Exception as e:
        print(f"Unexpected error getting country ID for '{country_name}': {e}")
        return False
    
def get_model_id(models, uid, model_name):
    """
    Gets the Odoo ID for a given model (e.g., 'crm.lead').
    """
    try:
        model_record = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
            'ir.model', 'search_read',
            [[('model', '=', model_name)]], {'fields': ['id'], 'limit': 1})
        if model_record:
            return model_record[0]['id']
        else:
            print(f"ERROR: Model '{model_name}' not found in Odoo.")
            return False
    except xmlrpc.client.Fault as e:
        print(f"Odoo RPC Error getting model ID for '{model_name}': {e.faultString}")
        return False
    except Exception as e:
        print(f"Unexpected error getting model ID for '{model_name}': {e}")
        return False

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the distance between two points on Earth using the Haversine formula.
    Latitudes and Longitudes are in decimal degrees.
    Returns distance in kilometers.
    """
    R = 6371  # Radius of Earth in kilometers

    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance

def find_closest_dealer(customer_lat, customer_lon):
    """
    Finds the closest dealer from the predefined DEALER_LOCATIONS.
    Returns a dictionary of the closest dealer's info or None if no dealers.
    """
    if not DEALER_LOCATIONS:
        print("No dealer locations defined.")
        return None

    closest_dealer = None
    min_distance = float('inf') # Initialize with a very large number

    for dealer in DEALER_LOCATIONS:
        dealer_lat = dealer["Latitude"]
        dealer_lon = dealer["Longitude"]
        
        distance = haversine_distance(customer_lat, customer_lon, dealer_lat, dealer_lon)
        
        if distance < min_distance:
            min_distance = distance
            closest_dealer = dealer
            closest_dealer["Distance_km"] = round(distance, 2) # Add distance to the result

    return closest_dealer


def get_or_create_tags(models, uid, tags):
    tag_ids = []
    for tag in tags:
        tag = tag.strip()
        if not tag:
            continue

        if tag == "Airblast Fans":
            tag = "Airblast"
        if tag == "DryIT Radial Flow":
            tag = "DryIT"
            print(f"DEBUG (connector): Transforming 'DryIT Radial Flow' to 'DryIT' for contact tag.")

        try:
            existing = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
                'res.partner.category', 'search_read',
                [[('name', '=', tag)]], {'fields': ['id'], 'limit': 1})
            if existing:
                tag_ids.append(existing[0]['id'])
            else:
                new_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
                    'res.partner.category', 'create', [{'name': tag}])
                tag_ids.append(new_id)
        except xmlrpc.client.Fault as e:
            print(f"Odoo RPC Error creating contact tag '{tag}': {e.faultString}")
        except Exception as e:
            print(f"Unexpected error creating contact tag '{tag}': {e}")
    return tag_ids


def get_or_create_opportunity_tags(models, uid, tags):
    """
    Gets or creates Odoo CRM Lead Tags (crm.tag) and returns their IDs.
    """
    tag_ids = []
    print(f"DEBUG (connector): get_or_create_opportunity_tags called with tags: {tags}")
    for tag in tags:
        tag = tag.strip()
        if not tag:
            print(f"DEBUG (connector): Skipping empty tag.")
            continue

        if tag == "Airblast Fans":
            tag = "Airblast"
            print(f"DEBUG (connector): Transforming 'Airblast Fans' to 'Airblast' for opportunity tag.")
        if tag == "DryIT Radial Flow":
            tag = "DryIT"
            print(f"DEBUG (connector): Transforming 'DryIT Radial Flow' to 'DryIT' for opportunity tag.")

        try:
            print(f"DEBUG (connector): Searching for opportunity tag: '{tag}'")
            existing = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
                'crm.tag', 'search_read',
                [[('name', '=', tag)]], {'fields': ['id'], 'limit': 1})
            if existing:
                tag_ids.append(existing[0]['id'])
                print(f"DEBUG (connector): Found existing tag '{tag}' with ID: {existing[0]['id']}")
            else:
                new_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
                    'crm.tag', 'create', [{'name': tag}])
                tag_ids.append(new_id)
                print(f"DEBUG (connector): Created new tag '{tag}' with ID: {new_id}")
        except xmlrpc.client.Fault as e:
            print(f"Odoo RPC Error getting/creating opportunity tag '{tag}': {e.faultString}")
        except Exception as e:
            print(f"Unexpected error getting/creating opportunity tag '{tag}': {e}")
    print(f"DEBUG (connector): Final tag_ids collected: {tag_ids}")
    return tag_ids


def create_odoo_contact(data):
    uid, models = connect_odoo()
    if not uid: return None

    tag_ids = get_or_create_tags(models, uid, data['Products Interest'])

    country_id = False
    state_id = False
    prov_state_input = data['Prov/State'].strip()

    if prov_state_input:
        state_id = get_state_id(models, uid, prov_state_input)
        
        country_name = STATE_TO_COUNTRY_MAP.get(prov_state_input, None)
        if country_name:
            country_id = get_country_id(models, uid, country_name)
        else:
            print(f"DEBUG: Unknown Prov/State '{prov_state_input}', country will be left blank.")
    else:
        print("DEBUG: No Prov/State provided, country will be left blank.")

    print(f"DEBUG: Country ID determined for contact: {country_id}")

    try:
        contact_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
            'res.partner', 'create', [{
                'name': data['Name'],
                'email': data['Email'],
                'phone': data['Phone'],
                'city': data['City'],
                'state_id': state_id,
                'country_id': country_id,
                'category_id': [(6, 0, tag_ids)] if tag_ids else False
            }])
        print(f"Contact created with ID: {contact_id}")
        return contact_id
    except xmlrpc.client.Fault as e:
        print(f"Odoo RPC Error creating contact: Code={e.faultCode}, Message={e.faultString}")
        return None
    except Exception as e:
        print(f"Unexpected error creating contact: {e}")
        return None

def update_odoo_contact(contact_id, data):
    uid, models = connect_odoo()
    if not uid: return False

    tag_ids = get_or_create_tags(models, uid, data['Products Interest'])

    country_id = False
    state_id = False
    prov_state_input = data['Prov/State'].strip()

    if prov_state_input:
        state_id = get_state_id(models, uid, prov_state_input)

        country_name = STATE_TO_COUNTRY_MAP.get(prov_state_input, None)
        if country_name:
            country_id = get_country_id(models, uid, country_name)
        else:
            print(f"DEBUG: Unknown Prov/State '{prov_state_input}', country will be left blank for update.")
    else:
        print("DEBUG: No Prov/State provided, country will be left blank for update.")

    print(f"DEBUG: Country ID determined for contact update: {country_id}")

    update_vals = {
        'name': data['Name'],
        'email': data['Email'],
        'phone': data['Phone'],
        'city': data['City'],
        'state_id': state_id,
        'country_id': country_id,
        'category_id': [(6, 0, tag_ids)] if tag_ids else False
    }
    try:
        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
            'res.partner', 'write', [[contact_id], update_vals])
        print(f"Contact ID {contact_id} updated.")
        return True
    except xmlrpc.client.Fault as e:
        print(f"Odoo RPC Error updating contact {contact_id}: Code={e.faultCode}, Message={e.faultString}")
        return False
    except Exception as e:
        print(f"Unexpected error updating contact {contact_id}: {e}")
        return False

def find_existing_contact(data):
    print("find_existing_contact() was called")
    uid, models = connect_odoo()
    domain = [('name', 'ilike', data['Name'])]
    
    print(f"Searching for name ilike: '{data['Name']}'")
    
    try:
        existing = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
            'res.partner', 'search_read',
            [domain], {'fields': ['id', 'name', 'email', 'phone'], 'limit': 1})
        
        print("Found result:", existing)
        return existing[0] if existing else None
    except xmlrpc.client.Fault as e:
        print(f"Odoo RPC Error finding contact: Code={e.faultCode}, Message={e.faultString}")
        return None
    except Exception as e:
        print(f"Unexpected error finding contact: {e}")
        return None

def create_odoo_opportunity(opportunity_data):
    """
    Creates a new opportunity in Odoo.
    opportunity_data is a dictionary containing opportunity details,
    e.g., {'name': 'Opportunity Name', 'partner_id': contact_id, 'user_id': sales_user_id}
    """
    uid, models = connect_odoo()
    if not uid:
        print("Failed to log in for opportunity creation.")
        return None
    try:
        new_opportunity_id = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'crm.lead',
            'create',
            [opportunity_data]
        )
        print(f"Opportunity created with ID: {new_opportunity_id}")
        return new_opportunity_id
    except xmlrpc.client.Fault as fault:
        print(f"Odoo RPC Error creating opportunity: Code={fault.faultCode}, Message={fault.faultString}")
        return None
    except Exception as e:
        print(f"Unexpected error creating opportunity in Odoo: {e}")
        return None

# --- NEW FUNCTION: Find Odoo User ID ---
def find_odoo_user_id(models, uid, user_name):
    """
    Finds the Odoo user ID by name.
    """
    try:
        user = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
            'res.users', 'search_read',
            [[('name', '=', user_name)]], {'fields': ['id'], 'limit': 1})
        if user:
            print(f"DEBUG (connector): Found user '{user_name}' with ID: {user[0]['id']}")
            return user[0]['id']
        else:
            print(f"DEBUG (connector): User '{user_name}' not found in Odoo.")
            return False
    except xmlrpc.client.Fault as e:
        print(f"Odoo RPC Error finding user '{user_name}': {e.faultString}")
        return False
    except Exception as e:
        print(f"Unexpected error finding user '{user_name}': {e}")
        return False

# --- NEW FUNCTION: Create Odoo Activity ---
def create_odoo_activity(models, uid, activity_data):
    """
    Creates a new activity in Odoo.
    activity_data is a dictionary containing activity details.
    """
    try:
        # Get the ID for the 'Follow up on email' activity type
        # It's good practice to get activity type by name, as IDs can vary
        activity_type = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
            'mail.activity.type', 'search_read',
            [[('name', '=', 'To-Do')]], {'fields': ['id'], 'limit': 1})
        
        activity_type_id = activity_type[0]['id'] if activity_type else False

        if not activity_type_id:
            print("ERROR (connector): 'Email' activity type not found in Odoo. Cannot create activity.")
            return False

        # Prepare activity data, adding activity_type_id
        activity_data['activity_type_id'] = activity_type_id

        new_activity_id = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'mail.activity',
            'create',
            [activity_data]
        )
        print(f"Activity created with ID: {new_activity_id}")
        return new_activity_id
    except xmlrpc.client.Fault as fault:
        print(f"Odoo RPC Error creating activity: Code={fault.faultCode}, Message={fault.faultString}")
        return False
    except Exception as e:
        print(f"Unexpected error creating activity in Odoo: {e}")
        return False
    
def find_existing_opportunity(opportunity_name):
    """
    Finds an existing opportunity in Odoo by its name.
    Returns a dictionary of the opportunity's info (id, name) or None.
    """
    uid, models = connect_odoo()
    if not uid:
        print("Failed to log in to Odoo for opportunity search.")
        return None
    try:
        domain = [('name', '=', opportunity_name)]
        existing = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
            'crm.lead', 'search_read',
            [domain], {'fields': ['id', 'name'], 'limit': 1})
            
        if existing:
            print(f"DEBUG (connector): Found existing opportunity: {existing[0]['name']} (ID: {existing[0]['id']})")
            return existing[0]
        else:
            print(f"DEBUG (connector): No existing opportunity found with name: '{opportunity_name}'")
            return None
    except xmlrpc.client.Fault as e:
        print(f"Odoo RPC Error finding opportunity '{opportunity_name}': {e.faultString}")
        return None
    except Exception as e:
        print(f"Unexpected error finding opportunity '{opportunity_name}': {e}")
        return None


def update_odoo_opportunity(opportunity_id, opportunity_data):
    """
    Updates an existing opportunity in Odoo.
    opportunity_data is a dictionary containing fields to update.
    """
    uid, models = connect_odoo()
    if not uid:
        print("Failed to log in to Odoo for opportunity update.")
        return False
    try:
        success = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'crm.lead',
            'write',
            [[opportunity_id], opportunity_data]
        )
        print(f"Opportunity ID {opportunity_id} updated: {success}")
        return success
    except xmlrpc.client.Fault as fault:
        print(f"Odoo RPC Error updating opportunity {opportunity_id}: Code={fault.faultCode}, Message={fault.faultString}")
        return False
    except Exception as e:
        print(f"Unexpected error updating opportunity {opportunity_id}: {e}")
        return False