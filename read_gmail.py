# run me first
# pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib openai
# to run
# python read_gmail.py

import os.path
import base64
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    return service

def get_messages(service, user_id='me'):
    """Get a list of Messages from the user's mailbox."""
    try:
        results = service.users().messages().list(userId=user_id, labelIds=['INBOX']).execute()
        messages = results.get('messages', [])
        return messages
    except Exception as error:
        print(f'An error occurred: {error}')
        return []

def read_message(service, user_id, msg_id):
    """Read an individual message."""
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id).execute()
        
        # Get the message parts
        payload = message['payload']
        parts = payload.get('parts', [])
        
        # If the message is simple (no parts)
        if 'body' in payload and payload['body'].get('data'):
            return base64.urlsafe_b64decode(payload['body']['data'].encode('ASCII')).decode('utf-8')
            
        # If the message has parts (multipart)
        for part in parts:
            if part['mimeType'] == 'text/plain':
                if 'data' in part['body']:
                    return base64.urlsafe_b64decode(part['body']['data'].encode('ASCII')).decode('utf-8')
                
        return "No text content found in message"
        
    except Exception as error:
        print(f'An error occurred: {error}')
        return None

def main():
    """Main function to read emails from Gmail."""
    service = authenticate_gmail()
    messages = get_messages(service)

    for message in messages:
        msg_id = message['id']
        msg_str = read_message(service, 'me', msg_id)
        print(f'Message ID: {msg_id}\nMessage: {msg_str}\n')

if __name__ == '__main__':
    main()
