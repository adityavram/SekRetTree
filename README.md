# SekRetTree
Automated Email Management System with AI-Powered Response Generation

## Features
- **Email Processing**
  - Reads emails from Gmail inbox
  - Summarizes email content using OpenAI GPT
  - Categorizes emails into three types:
    1. Requires human response
    2. Can be auto-responded
    3. No response needed

- **Automated Responses**
  - Generates contextual responses using GPT for suitable emails
  - Maintains professional tone and includes appropriate signatures
  - Sends responses while maintaining email threading

- **Smart Email Organization**
  - Flags important emails requiring human attention
  - Creates custom labels for better visibility
  - Moves no-response-needed emails to spam
  - Stars and marks priority for urgent emails

## Prerequisites
- Python 3.8 or higher
- Gmail account with API access enabled
- OpenAI API key

## Installation

1. Clone the repository:
bash
git clone https://github.com/yourusername/sekretree.git
cd sekretree

2. Install dependencies:
bash
pip install -r requirements.txt

3. Set up Gmail API:
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project
   - Enable Gmail API
   - Create credentials (OAuth 2.0 Client ID)
   - Download credentials and save as `credentials.json` in project root

4. Set up environment variables:
   - Create a `.env` file in the project root
   - Add your OpenAI API key and other configurations:

4. Run the script:
bash
python main.py

2. On first run:
   - Browser will open for Gmail authentication
   - Grant necessary permissions
   - Token will be saved locally for future use

## File Structure
- `main.py`: Main execution script
- `read_gmail.py`: Gmail API integration
- `summarize.py`: Email summarization using GPT
- `categorize.py`: Email classification logic
- `respond.py`: Response generation and sending
- `flag.py`: Email flagging and organization

## Configuration
- Adjust `MAX_EMAILS` in `.env` to control batch size
- Modify model settings in `.env` for different GPT versions
- Customize response templates in `respond.py`
- Adjust categorization rules in `categorize.py`

## Security Notes
- Never commit `.env` or `credentials.json` to version control
- Store API keys and credentials securely
- Review auto-generated responses before enabling auto-send
- Test thoroughly with non-critical emails first

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- OpenAI for GPT API
- Google for Gmail API
- All contributors and testers

## Support
For support, please open an issue in the GitHub repository.
