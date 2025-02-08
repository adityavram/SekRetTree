import os
from openai import OpenAI
from read_gmail import authenticate_gmail, get_messages, read_message

def summarize_text(text, client):
    """Summarize the given text using OpenAI API."""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes emails concisely."},
                {"role": "user", "content": f"Please summarize this email in 2-3 sentences:\n\n{text}"}
            ],
            max_tokens=150
        )
        return response.choices[0].message.content
    except Exception as error:
        print(f"Error in summarization: {error}")
        return None

def main():
    # Initialize OpenAI client
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("Please set your OPENAI_API_KEY environment variable")
    client = OpenAI(api_key=api_key)

    # Get Gmail service
    service = authenticate_gmail()
    
    # Get recent messages (limit to 5 for testing)
    messages = get_messages(service)[:5]
    
    print("Processing emails...\n")
    
    for message in messages:
        msg_id = message['id']
        email_content = read_message(service, 'me', msg_id)
        
        if email_content:
            print("=" * 50)
            print("Original Email:")
            print(email_content[:200] + "..." if len(email_content) > 200 else email_content)
            print("\nSummary:")
            summary = summarize_text(email_content, client)
            print(summary if summary else "Could not generate summary")
            print("=" * 50 + "\n")

if __name__ == '__main__':
    main() 