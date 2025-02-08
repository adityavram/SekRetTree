def check_packages():
    """Check and install required packages."""
    import subprocess
    import sys
    
    def install_package(package):
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
    required_packages = {
        'python-dotenv': 'dotenv',
        'openai': 'openai',
        'google-auth-oauthlib': 'google_auth_oauthlib',
        'google-auth-httplib2': 'google_auth_httplib2',
        'google-api-python-client': 'googleapiclient'
    }
    
    for package, import_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            print(f"Installing {package}...")
            install_package(package)
            print(f"Successfully installed {package}")

# Run package check before imports
check_packages()

import os
from dotenv import load_dotenv
from openai import OpenAI
from read_gmail import authenticate_gmail, get_messages, read_message
from datetime import datetime
import logging
from respond import EmailResponder
from flag import EmailFlagger

# Rest of your existing code... 

class EmailProcessor:
    def __init__(self):
        load_dotenv()
        self.setup_clients()
        self.categorizer = EmailCategorizer(self.openai_client)
        self.responder = EmailResponder(self.openai_client, self.gmail_service)
        self.flagger = EmailFlagger(self.gmail_service)

    def process_emails(self):
        """Main function to process emails."""
        try:
            messages = get_messages(self.gmail_service)[:self.max_emails]
            logging.info(f"Processing {len(messages)} emails")
            
            results = []
            for message in messages:
                msg_id = message['id']
                email_content = read_message(self.gmail_service, 'me', msg_id)
                
                if email_content:
                    summary = self.summarize_email(email_content)
                    category_info = self.categorizer.categorize_email(email_content)
                    
                    result = {
                        'id': msg_id,
                        'content': email_content,
                        'summary': summary,
                        'category': category_info['category'],
                        'category_explanation': category_info['explanation'],
                        'processed_at': datetime.now().isoformat()
                    }
                    
                    # Handle auto-responses
                    if category_info['category'] == 'AUTO_REPLY':
                        response_text = self.responder.generate_response(email_content, summary)
                        if response_text:
                            send_result = self.responder.send_response(msg_id, response_text)
                            result['auto_response'] = {
                                'response_text': response_text,
                                'send_success': send_result['success'],
                                'send_details': send_result
                            }
                    
                    # Flag important emails needing human response
                    elif category_info['category'] == 'HUMAN_NEEDED':
                        flag_result = self.flagger.flag_important_email(msg_id)
                        result['flag_status'] = flag_result
                    
                    # Move no-response emails to spam
                    elif category_info['category'] == 'NO_RESPONSE':
                        spam_result = self.flagger.mark_as_spam(msg_id)
                        result['spam_status'] = spam_result
                    
                    results.append(result)
                    
                    # Print results
                    print("\n" + "="*50)
                    print("Original Email:")
                    print(email_content[:200] + "..." if len(email_content) > 200 else email_content)
                    print("\nSummary:")
                    print(summary if summary else "Could not generate summary")
                    print("\nCategory:")
                    print(f"{category_info['category']}: {category_info['explanation']}")
                    if result.get('auto_response'):
                        print("\nAuto-Response:")
                        print(result['auto_response']['response_text'])
                    if result.get('flag_status'):
                        print("\nFlag Status:")
                        print(result['flag_status']['message'] if result['flag_status']['success'] 
                              else f"Failed to flag: {result['flag_status'].get('error')}")
                    if result.get('spam_status'):
                        print("\nSpam Status:")
                        print(result['spam_status']['message'] if result['spam_status']['success'] 
                              else f"Failed to mark as spam: {result['spam_status'].get('error')}")
                    print("="*50)
            
            # Print statistics
            stats = self.categorizer.get_category_stats(results)
            print("\nCategory Statistics:")
            for category, count in stats.items():
                if count > 0:
                    print(f"{category}: {count}")
                    
            return results
            
        except Exception as error:
            logging.error(f"Error processing emails: {error}")
            raise 