from openai import OpenAI
import base64
from email.mime.text import MIMEText
import logging

class EmailResponder:
    def __init__(self, openai_client, gmail_service):
        self.client = openai_client
        self.gmail_service = gmail_service
        
    def generate_response(self, email_content, email_summary=None):
        """Generate an appropriate response using OpenAI."""
        try:
            context = f"""Original Email: {email_content}
            Summary: {email_summary if email_summary else 'Not provided'}"""
            
            prompt = """Generate a professional and helpful email response. The response should:
            1. Be concise but friendly
            2. Address the main points/questions
            3. Use appropriate tone based on the original email
            4. Include a professional signature
            5. Be self-contained (recipient shouldn't need to see original email)
            
            Context:
            {context}"""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional email assistant. Generate helpful, clear, and appropriate responses."},
                    {"role": "user", "content": prompt.format(context=context)}
                ],
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as error:
            logging.error(f"Error generating response: {error}")
            return None

    def send_response(self, original_message_id, response_text):
        """Send the response email using Gmail API."""
        try:
            # Get the original message to extract thread ID and subject
            original_message = self.gmail_service.users().messages().get(
                userId='me', 
                id=original_message_id
            ).execute()
            
            # Create message
            message = MIMEText(response_text)
            thread_id = original_message['threadId']
            
            # Extract subject and recipients from original message
            headers = {header['name']: header['value'] for header in original_message['payload']['headers']}
            original_subject = headers.get('Subject', '')
            if not original_subject.lower().startswith('re:'):
                original_subject = f"Re: {original_subject}"
            
            to_address = headers.get('From')  # Original sender becomes recipient
            
            message['to'] = to_address
            message['subject'] = original_subject
            
            # Encode the message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send the message
            sent_message = self.gmail_service.users().messages().send(
                userId='me',
                body={
                    'raw': raw_message,
                    'threadId': thread_id
                }
            ).execute()
            
            return {
                'success': True,
                'message_id': sent_message['id'],
                'thread_id': thread_id
            }
            
        except Exception as error:
            logging.error(f"Error sending response: {error}")
            return {
                'success': False,
                'error': str(error)
            }

    def process_auto_responses(self, categorized_emails):
        """Process all emails marked for auto-response."""
        results = []
        
        for email in categorized_emails:
            if email['category'] == 'AUTO_REPLY':
                logging.info(f"Generating auto-response for email {email['id']}")
                
                # Generate response
                response_text = self.generate_response(
                    email['content'],
                    email.get('summary')
                )
                
                if response_text:
                    # Send response
                    send_result = self.send_response(email['id'], response_text)
                    
                    results.append({
                        'email_id': email['id'],
                        'response_text': response_text,
                        'send_success': send_result['success'],
                        'send_details': send_result
                    })
                    
                    # Log results
                    if send_result['success']:
                        logging.info(f"Successfully sent auto-response to email {email['id']}")
                    else:
                        logging.error(f"Failed to send auto-response to email {email['id']}")
                        
        return results

def main():
    """Test function to demonstrate response generation and sending."""
    import os
    from dotenv import load_dotenv
    from read_gmail import authenticate_gmail
    
    # Load environment variables
    load_dotenv()
    
    # Initialize clients
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    gmail_service = authenticate_gmail()
    
    # Create responder
    responder = EmailResponder(client, gmail_service)
    
    # Test email content
    test_email = {
        'id': 'test_id',
        'content': """Hello, I would like to confirm my appointment for next week.
        Can you please let me know if Tuesday at 2 PM is still available?
        Thanks, John""",
        'category': 'AUTO_REPLY',
        'summary': 'John is requesting confirmation for a Tuesday 2 PM appointment next week.'
    }
    
    # Generate response
    response = responder.generate_response(test_email['content'], test_email['summary'])
    
    print("\nGenerated Response:")
    print("="*50)
    print(response)
    print("="*50)
    
    # Note: Actual sending is commented out for testing
    # send_result = responder.send_response(test_email['id'], response)
    # print("\nSend Result:", send_result)

if __name__ == "__main__":
    main() 