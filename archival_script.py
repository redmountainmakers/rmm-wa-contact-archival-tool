import os
import json
import requests
import base64
import logging
import subprocess
from datetime import datetime, timezone
from dateutil import parser

api_key = os.environ.get("WA_API_KEY")

log_file_path = 'wa_contact_archive.log'
logging.basicConfig(level=logging.INFO, filename= log_file_path, filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')

def get_access_token(api_key):
    """Obtains and returns an access token for the Wild Apricot API."""
    auth_url = 'https://oauth.wildapricot.org/auth/token'
    encoded_key = base64.b64encode(f'APIKEY:{api_key}'.encode()).decode()
    auth_headers = {'Authorization': f'Basic {encoded_key}', 'Content-Type': 'application/x-www-form-urlencoded'}
    auth_data = {'grant_type': 'client_credentials', 'scope': 'auto'}
    auth_response = requests.post(auth_url, headers=auth_headers, data=auth_data)
    return auth_response.json().get('access_token')

def get_account_id(headers):
    """Retrieves the account ID."""
    api_base_url = 'https://api.wildapricot.org/v2.2'
    response = requests.get(f"{api_base_url}/accounts", headers=headers)
    if response.status_code != 200:
        logging.error(f"Error: Unable to retrieve account details. Status code: {response.status_code}")
        return None
    return response.json()[0]['Id']

def get_contact_info(contact_id, access_token):
    """Retrieves the email address and first name of a contact given a contact ID."""
    api_base_url = 'https://api.wildapricot.org/v2.1'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    # Make an API request to retrieve the account details
    account_response = requests.get(f'{api_base_url}/accounts', headers=headers)
    if account_response.status_code != 200:
        logging.error(f'Error: Unable to retrieve account details. Status code: {account_response.status_code}')
        return

    account_id = account_response.json()[0]['Id']

    # Make an API request to retrieve the contact details
    contact_response = requests.get(f'{api_base_url}/accounts/{account_id}/contacts/{contact_id}', headers=headers)
    if contact_response.status_code != 200:
        logging.error(f'Error: Unable to retrieve contact details. Status code: {contact_response.status_code}')
        return

    contact_details = contact_response.json()

    # Get the email address, first name, and membership status from the contact details
    email = contact_details.get('Email', 'Unknown')
    first_name = contact_details.get('FirstName', 'Unknown')

    return email, first_name

def set_contact_to_archived(contact_id, access_token):
    api_base_url = 'https://api.wildapricot.org/v2.1'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    # Make an API request to retrieve the account details
    account_response = requests.get(f'{api_base_url}/accounts', headers=headers)
    if account_response.status_code != 200:
        logging.error(f'Error: Unable to retrieve account details. Status code: {account_response.status_code}')
        return

    account_id = account_response.json()[0]['Id']

    contact_response = requests.get(f'{api_base_url}/accounts/{account_id}/contacts/{contact_id}', headers=headers)
    if contact_response.status_code != 200:
        logging.error(f'Error: Unable to retrieve contact details. Status code: {contact_response.status_code}')
        return

    contact_data = contact_response.json()

   

    for field in contact_data['FieldValues']:
        if field['SystemCode'] == 'IsArchived':
            field['Value'] = True
        if field['SystemCode'] == 'Notes':
            current_notes = field['Value']
            # Add new line to the notes with the current date and "RMM Archival Bot"
            new_note = f"\n\r\nMember archived on {datetime.now().strftime('%m/%d/%Y')} by RMM Archival Bot"
            field['Value'] = current_notes + new_note
    

    # Send the updated data back to the API
    update_response = requests.put(f'{api_base_url}/accounts/{account_id}/contacts/{contact_id}', headers=headers, data=json.dumps(contact_data))
    if update_response.status_code != 200:
        logging.error(f'Error: Unable to update contact. Status code: {update_response.status_code}')
        return

    return "Contact archived successfully"

    formatted_data = []

    # Basic contact information
    formatted_data.append(f"First Name: {contact_data.get('FirstName', 'Unknown')}")
    formatted_data.append(f"Last Name: {contact_data.get('LastName', 'Unknown')}")
    formatted_data.append(f"Email: {contact_data.get('Email', 'Unknown')}")
    formatted_data.append(f"Membership Level: {contact_data.get('MembershipLevel', {}).get('Name', 'Unknown')}")

    # Detailed field values
    formatted_data.append("\nDetailed Fields:")
    for field in contact_data.get('FieldValues', []):
        field_name = field.get('FieldName', 'Unknown Field')
        field_value = field.get('Value', 'Unknown Value')
        formatted_data.append(f"  {field_name}: {field_value}")

    # Return the formatted data
    return '\n'.join(formatted_data)

def num_members(access_token):
    """Finds a contact by Discord username."""
    api_base_url = 'https://api.wildapricot.org/v2.2'
    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json', 'Accept': 'application/json'}
    
    account_id = get_account_id(headers)
    if not account_id:
        return None

    filter_query = f"$filter='Member' eq 'True'"
    contacts_url = f"{api_base_url}/accounts/{account_id}/contacts?$async=false&{filter_query}"
    
    contacts_response = requests.get(contacts_url, headers=headers)

    if contacts_response.status_code != 200:
        logging.error(f"Error: Unable to retrieve contacts. Status code: {contacts_response.status_code}")
        return None
    else:
        return len(contacts_response.json().get("Contacts", []))

def num_contacts(access_token):
    """Finds a contact by Discord username."""
    api_base_url = 'https://api.wildapricot.org/v2.2'
    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json', 'Accept': 'application/json'}
    
    account_id = get_account_id(headers)
    if not account_id:
        return None

    filter_query = f"$filter='IsArchived' eq 'False'"
    contacts_url = f"{api_base_url}/accounts/{account_id}/contacts?$async=false&{filter_query}"
    
    contacts_response = requests.get(contacts_url, headers=headers)

    if contacts_response.status_code != 200:
        logging.error(f"Error: Unable to retrieve contacts. Status code: {contacts_response.status_code}")
        return None
    else:
        return len(contacts_response.json().get("Contacts", []))

def contacts_w_registrations(access_token):
    """Finds a contact by Discord username."""
    api_base_url = 'https://api.wildapricot.org/v2.2'
    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json', 'Accept': 'application/json'}
    
    account_id = get_account_id(headers)
    if not account_id:
        return None

    filter_query = f"$filter='Member' ne 'True' and 'IsArchived' eq 'False' and 'Balance' eq '0.0'"
    contacts_url = f"{api_base_url}/accounts/{account_id}/contacts?$async=false&{filter_query}"
    
    contacts_response = requests.get(contacts_url, headers=headers)

    contacts = contacts_response.json().get("Contacts", [])
    
    contacts_w_registration = []

    for contact in contacts:
        upcoming_event = has_upcoming_event_registrations(contact['Id'], access_token)

        if upcoming_event:
            contacts_w_registration.append(contact['Id'])

    if contacts_response.status_code != 200:
        logging.error(f"Error: Unable to retrieve contacts. Status code: {contacts_response.status_code}")
        return None
    else:
        return len(contacts_w_registration)

def contacts_w_balance(access_token):
    """Finds a contact by Discord username."""
    api_base_url = 'https://api.wildapricot.org/v2.2'
    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json', 'Accept': 'application/json'}
    
    account_id = get_account_id(headers)
    if not account_id:
        return None

    filter_query = f"$filter='Balance' ne '0.0'"
    contacts_url = f"{api_base_url}/accounts/{account_id}/contacts?$async=false&{filter_query}"
    
    contacts_response = requests.get(contacts_url, headers=headers)

    if contacts_response.status_code != 200:
        logging.error(f"Error: Unable to retrieve contacts. Status code: {contacts_response.status_code}")
        return None
    else:
        return len(contacts_response.json().get("Contacts", []))

def return_archival_candidates(access_token):
    """Finds a contact by Discord username."""
    api_base_url = 'https://api.wildapricot.org/v2.2'
    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json', 'Accept': 'application/json'}
    
    account_id = get_account_id(headers)
    if not account_id:
        return None

    filter_query = f"$filter='Member' eq 'False' and 'IsArchived' eq 'False' and 'Balance' eq '0.0'"
    contacts_url = f"{api_base_url}/accounts/{account_id}/contacts?$async=false&{filter_query}"
    
    contacts_response = requests.get(contacts_url, headers=headers)

    contacts = contacts_response.json().get("Contacts", [])

    contacts.sort(key=get_last_login_date, reverse=False)

    
    archival_candidates = []

    for contact in contacts:
        upcoming_event = has_upcoming_event_registrations(contact['Id'], access_token)

        if not upcoming_event:
            archival_candidates.append(contact['Id'])

    if contacts_response.status_code != 200:
        logging.error(f"Error: Unable to retrieve contacts. Status code: {contacts_response.status_code}")
        return None
    else:
        return archival_candidates

def has_upcoming_event_registrations(contact_id, access_token):
    api_base_url = 'https://api.wildapricot.org/v2.1'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    # Retrieve the account details
    account_response = requests.get(f'{api_base_url}/accounts', headers=headers)
    if account_response.status_code != 200:
        logging.error(f'Error: Unable to retrieve account details. Status code: {account_response.status_code}')
        return False

    account_id = account_response.json()[0]['Id']

    # Retrieve event registrations for the contact
    registrations_url = f"{api_base_url}/accounts/{account_id}/eventregistrations?contactId={contact_id}"
    registrations_response = requests.get(registrations_url, headers=headers)

    if registrations_response.status_code != 200:
        logging.error(f'Error: Unable to retrieve event registrations. Status code: {registrations_response.status_code}')
        return False

    registrations = registrations_response.json()

    # Check if any of the event start dates are in the future

    for registration in registrations:
        event_start_date = registration.get('Event', {}).get('StartDate')
        if event_start_date:
            event_start_date = parser.parse(event_start_date)
            current_time = datetime.now(event_start_date.tzinfo)
            if event_start_date > current_time:
                return True

    return False

def get_last_login_date(contact):
    """Extracts and returns the last login date from the contact's FieldValues."""
    for field in contact.get('FieldValues', []):
        if field['SystemCode'] == 'LastLoginDate':
            last_login_str = field.get('Value')
            if last_login_str:
                # Parse the datetime string and make it offset-aware
                last_login_date = parser.parse(last_login_str)
                if last_login_date.tzinfo is None:
                    last_login_date = last_login_date.replace(tzinfo=timezone.utc)
                return last_login_date
    return datetime.min.replace(tzinfo=timezone.utc)

def cleanup_log_file():
    subprocess.run(['git', 'add', log_file_path])
    subprocess.run(['git', 'commit', '-m', 'Processed events from Wild Apricot to discord'])
    subprocess.run(['git', 'push'])

access_token = get_access_token(api_key)

logging.info("Starting archival script")

num_contacts = num_contacts(access_token)

contact_target = 190

removal_target = num_contacts - contact_target

if num_contacts > contact_target:
    logging.info(f"Currently at {num_contacts} contacts. Target is {contact_target}, attempting to remove {removal_target} contacts.")
else:
    logging.info(f"Currently at {num_contacts} contacts. Target is {contact_target}, no action required. Exiting")
    cleanup_log_file()
    exit()

number_of_members = num_members(access_token)

num_non_members_with_a_balance = contacts_w_balance(access_token)

num_non_members_future_registration = contacts_w_registrations(access_token)

minimum_contacts = number_of_members + num_non_members_with_a_balance + num_non_members_future_registration

contact_margin = contact_target - minimum_contacts - 10 #10 is a buffer

if contact_margin < 0:
    logging.info(f"Warning: Currently at {minimum_contacts} contacts. Target is {contact_target}, we have more contacts than the target. Need to consider upgrading our plan.")
    cleanup_log_file()
    exit()
else:
    logging.info(f"Currently at {minimum_contacts} minimum contacts. Target is {contact_target}, we have {contact_margin} contacts margin.\nContinuing to remove {removal_target} contacts.")

logging.info(f"Minimum contact makeup:\nNumber of members: {number_of_members}\nNumber of non-members with a balance: {num_non_members_with_a_balance}\nNumber of non-members with future registrations: {num_non_members_future_registration}")

archival_candidates = return_archival_candidates(access_token)

logging.info(f"{len(archival_candidates)} total candidates available for archive")

num = 0

for contact in archival_candidates:
    num += 1
    if num > removal_target:
        logging.info("Exiting after removing target contacts")
        cleanup_log_file()
        exit()
    logging.info(f"Archiving contact {contact}")
    set_contact_to_archived(contact, access_token)

cleanup_log_file()
