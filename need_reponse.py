# run me first
# pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib openai
# to run
# python need_reponse.py

import openai
import imaplib
import email
from email.header import decode_header
import os

# Set your OpenAI API key here
OPENAI_API_KEY = 'your-openai-api-key'
openai.api_key = OPENAI_API_KEY

def should_respond_to_email(email_text):
    """Use OpenAI's GPT to determine if an email merits a response."""
    prompt = f"The following is an email message:\n\n{email_text}\n\nDetermine if this email needs a response. Respond with 'Y' for Yes and 'N' for No."
    response = client.chat.completions.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=5,
        n=1,
        stop=None,
        temperature=0.5,
    )
    return response.choices[0].text.strip()

def connect_to_gmail(email_address, app_password):
    """Connect to Gmail using IMAP."""
    imap_server = "imap.gmail.com"
    imap = imaplib.IMAP4_SSL(imap_server)
    imap.login(email_address, app_password)
    return imap

def read_emails(imap, folder="INBOX", max_emails=5):
    """Read emails from specified folder."""
    imap.select(folder)
    _, message_numbers = imap.search(None, "ALL")
    
    emails = []
    for num in message_numbers[0].split()[-max_emails:]:
        _, msg_data = imap.fetch(num, "(RFC822)")
        email_body = msg_data[0][1]
        message = email.message_from_bytes(email_body)
        
        subject = decode_header(message["subject"])[0][0]
        if isinstance(subject, bytes):
            subject = subject.decode()
            
        body = ""
        if message.is_multipart():
            for part in message.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = message.get_payload(decode=True).decode()
            
        emails.append({
            "subject": subject,
            "body": body
        })
    
    return emails

def main():
    # Email credentials
    EMAIL_ADDRESS = "your-email@gmail.com"
    APP_PASSWORD = "your-app-password"  # Generate this in Google Account settings
    
    # Connect to email
    imap = connect_to_gmail(EMAIL_ADDRESS, APP_PASSWORD)
    
    # Read recent emails
    emails = read_emails(imap)
    
    # Process each email
    for email_data in emails:
        email_text = f"Subject: {email_data['subject']}\n\n{email_data['body']}"
        decision = should_respond_to_email(email_text)
        print(f"Subject: {email_data['subject']}")
        print(f"Response needed: {decision}\n")
    
    # Cleanup
    imap.logout()

if __name__ == '__main__':
    main()
