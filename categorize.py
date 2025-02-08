from openai import OpenAI
import logging

class EmailCategorizer:
    def __init__(self, openai_client):
        self.client = openai_client
        
    def categorize_email(self, email_content):
        """
        Categorize email into one of three categories:
        1. Requires human response
        2. Can be auto-responded
        3. No response needed
        """
        try:
            prompt = """Analyze this email and categorize it into one of these categories:
            1. HUMAN_NEEDED: Requires personal attention and human response
            2. AUTO_REPLY: Can be handled with an automated response
            3. NO_RESPONSE: No response required
            
            Consider these guidelines:
            - HUMAN_NEEDED: Complex inquiries, important business matters, personal matters, 
              negotiations, complaints, or anything requiring human judgment
            - AUTO_REPLY: Simple inquiries, confirmations, routine requests, status updates, 
              or anything with standard/predictable responses
            - NO_RESPONSE: FYI emails, newsletters, marketing, notifications, or spam
            
            Respond with only the category (HUMAN_NEEDED, AUTO_REPLY, or NO_RESPONSE) 
            followed by a brief explanation.
            
            Email content:
            {email_content}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert email analyst who categorizes emails accurately."},
                    {"role": "user", "content": prompt.format(email_content=email_content)}
                ],
                temperature=0.3  # Lower temperature for more consistent categorization
            )
            
            # Extract category and explanation
            result = response.choices[0].message.content.strip()
            category = result.split('\n')[0].strip()  # First line contains the category
            explanation = '\n'.join(result.split('\n')[1:]).strip()  # Remaining lines are explanation
            
            return {
                'category': category,
                'explanation': explanation,
                'original_content': email_content[:200] + '...' if len(email_content) > 200 else email_content
            }
            
        except Exception as error:
            logging.error(f"Error in categorization: {error}")
            return {
                'category': 'ERROR',
                'explanation': f"Error during categorization: {str(error)}",
                'original_content': email_content[:200]
            }

    def get_category_stats(self, categorized_emails):
        """Generate statistics about email categories."""
        stats = {
            'HUMAN_NEEDED': 0,
            'AUTO_REPLY': 0,
            'NO_RESPONSE': 0,
            'ERROR': 0
        }
        
        for email in categorized_emails:
            stats[email['category']] = stats.get(email['category'], 0) + 1
            
        return stats

def main():
    """Test function to demonstrate categorization."""
    import os
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    # Initialize OpenAI client
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # Create categorizer
    categorizer = EmailCategorizer(client)
    
    # Test emails
    test_emails = [
        """Dear Support, I've been having issues with my account for the past week. 
        None of my previous tickets have been answered. This is urgent as it's affecting my business. 
        Please help resolve this immediately. Best regards, John""",
        
        """Thank you for your purchase! Your order #12345 has been confirmed and will be shipped within 2 business days. 
        Track your order at: tracking.example.com""",
        
        """Weekly Newsletter: Check out our latest updates and features! 
        Click here to learn more about our upcoming events."""
    ]
    
    # Process test emails
    results = []
    for email in test_emails:
        result = categorizer.categorize_email(email)
        results.append(result)
        print("\n" + "="*50)
        print(f"Category: {result['category']}")
        print(f"Explanation: {result['explanation']}")
        print(f"Original: {result['original_content']}")
        
    # Print statistics
    print("\nCategory Statistics:")
    stats = categorizer.get_category_stats(results)
    for category, count in stats.items():
        if count > 0:
            print(f"{category}: {count}")

if __name__ == "__main__":
    main() 