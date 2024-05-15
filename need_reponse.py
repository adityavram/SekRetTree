import openai

# Set your OpenAI API key here
OPENAI_API_KEY = 'your-openai-api-key'
openai.api_key = OPENAI_API_KEY

def should_respond_to_email(email_text):
    """Use OpenAI's GPT to determine if an email merits a response."""
    prompt = f"The following is an email message:\n\n{email_text}\n\nDetermine if this email needs a response. Respond with 'Y' for Yes and 'N' for No."
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=5,
        n=1,
        stop=None,
        temperature=0.5,
    )
    return response.choices[0].text.strip()

def main():
    email_text = """Subject: Meeting Reminder

    Hi team,

    Just a reminder about the meeting tomorrow at 10 AM.

    Regards,
    John Doe
    """
    
    decision = should_respond_to_email(email_text)
    print(f"Response needed: {decision}")

if __name__ == '__main__':
    main()
