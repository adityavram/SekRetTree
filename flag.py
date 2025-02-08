import logging
from googleapiclient.errors import HttpError

class EmailFlagger:
    def __init__(self, gmail_service):
        self.gmail_service = gmail_service
        self.important_label_id = self._get_or_create_label()

    def _get_or_create_label(self):
        """Get or create a custom label for important emails."""
        try:
            # Try to find existing label
            results = self.gmail_service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            
            for label in labels:
                if label['name'] == 'NEEDS_HUMAN_RESPONSE':
                    return label['id']
            
            # Create new label if it doesn't exist
            label_object = {
                'name': 'NEEDS_HUMAN_RESPONSE',
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show',
                'backgroundColor': '#fb4c2f',  # Red background
                'textColor': '#ffffff'         # White text
            }
            
            created_label = self.gmail_service.users().labels().create(
                userId='me',
                body=label_object
            ).execute()
            
            logging.info("Created new label: NEEDS_HUMAN_RESPONSE")
            return created_label['id']
            
        except Exception as error:
            logging.error(f"Error managing labels: {error}")
            return None

    def flag_important_email(self, message_id):
        """Flag an email as important and needing human response."""
        try:
            # Mark as important
            self.gmail_service.users().messages().modify(
                userId='me',
                id=message_id,
                body={
                    'addLabelIds': ['IMPORTANT', self.important_label_id],
                    'removeLabelIds': ['UNIMPORTANT']
                }
            ).execute()
            
            # Star the message
            self.gmail_service.users().messages().modify(
                userId='me',
                id=message_id,
                body={
                    'addLabelIds': ['STARRED']
                }
            ).execute()
            
            return {
                'success': True,
                'message': f'Email {message_id} flagged as important and requiring human response'
            }
            
        except HttpError as error:
            logging.error(f"Error flagging email {message_id}: {error}")
            return {
                'success': False,
                'error': str(error)
            }

    def mark_as_spam(self, message_id):
        """Move an email to spam folder."""
        try:
            # Move to spam
            self.gmail_service.users().messages().modify(
                userId='me',
                id=message_id,
                body={
                    'addLabelIds': ['SPAM'],
                    'removeLabelIds': ['INBOX', 'UNSPAM']
                }
            ).execute()
            
            return {
                'success': True,
                'message': f'Email {message_id} marked as spam'
            }
            
        except HttpError as error:
            logging.error(f"Error marking email as spam {message_id}: {error}")
            return {
                'success': False,
                'error': str(error)
            }

    def process_emails(self, categorized_emails):
        """Process all emails based on their category."""
        results = []
        
        for email in categorized_emails:
            result = {
                'email_id': email['id'],
                'category': email['category']
            }
            
            if email['category'] == 'HUMAN_NEEDED':
                logging.info(f"Flagging email {email['id']} as needing human response")
                flag_result = self.flag_important_email(email['id'])
                result.update({
                    'action': 'flag_important',
                    'success': flag_result['success'],
                    'details': flag_result
                })
                
            elif email['category'] == 'NO_RESPONSE':
                logging.info(f"Moving email {email['id']} to spam")
                spam_result = self.mark_as_spam(email['id'])
                result.update({
                    'action': 'mark_spam',
                    'success': spam_result['success'],
                    'details': spam_result
                })
            
            results.append(result)
            
            if result['success']:
                logging.info(f"Successfully processed email {email['id']}")
            else:
                logging.error(f"Failed to process email {email['id']}")
        
        return results

def main():
    """Test function to demonstrate email flagging and spam marking."""
    import os
    from dotenv import load_dotenv
    from read_gmail import authenticate_gmail
    
    # Load environment variables
    load_dotenv()
    
    # Initialize Gmail service
    gmail_service = authenticate_gmail()
    
    # Create flagger
    flagger = EmailFlagger(gmail_service)
    
    # Test data
    test_emails = [
        {
            'id': 'test-message-id-1',  # Replace with actual message ID for testing
            'category': 'HUMAN_NEEDED',
            'content': 'Important test email'
        },
        {
            'id': 'test-message-id-2',  # Replace with actual message ID for testing
            'category': 'NO_RESPONSE',
            'content': 'Marketing newsletter'
        }
    ]
    
    # Process test emails
    results = flagger.process_emails(test_emails)
    
    # Print results
    for result in results:
        print(f"\nResult for email {result['email_id']}:")
        print(f"Category: {result['category']}")
        print(f"Action: {result['action']}")
        print(f"Success: {result['success']}")
        if not result['success']:
            print(f"Error: {result['details'].get('error')}")

if __name__ == "__main__":
    main() 