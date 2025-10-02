# 21 Questions Game - Instructions

## Project Overview

This is a Flask-based web application that implements the classic "21 Questions" game using AWS Bedrock and Claude AI. The AI thinks of a secret word, and players have up to 21 questions to guess it.

## Features

- **AI-Powered Word Generation**: Uses Claude AI to generate random secret words
- **Smart Answer System**: AI referee provides "yes", "no", or "unclear" responses
- **Multiple Guess Formats**: Supports various question formats like "is it a dog?", "dog", etc.
- **Game State Management**: Tracks question count and game progress
- **Reveal Command**: Players can reveal the word at any time

## Prerequisites

### 1. AWS Account Setup
- AWS account with Bedrock access
- IAM user with `bedrock:InvokeModel` permissions
- AWS credentials configured (via AWS CLI, environment variables, or IAM roles)

### 2. Python Environment
- Python 3.8 or higher
- Virtual environment (recommended)

## Installation

### 1. Clone/Download the Project
```bash
git clone <your-repository-url>
cd twentyonebe
```

### 2. Create Virtual Environment
```bash
python -m venv venv
```

### 3. Activate Virtual Environment
**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

## AWS Configuration

### Option 1: AWS CLI Configuration
```bash
aws configure
```
Enter your:
- AWS Access Key ID
- AWS Secret Access Key
- Default region: `us-east-1`
- Default output format: `json`

### Option 2: Environment Variables
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

### Option 3: IAM Roles (for EC2/Lambda deployment)
Attach an IAM role with Bedrock permissions to your compute instance.

## Running the Application

### Local Development
```bash
python main.py
```
The server will start on `http://localhost:5000`

### Production Deployment
For production, use a WSGI server like Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

## API Endpoints

### 1. Start New Game
**POST** `/start_game`

**Response:**
```json
{
    "message": "Game started!",
    "secret_word_length": 5
}
```

### 2. Ask Question
**POST** `/ask`

**Request Body:**
```json
{
    "question": "Is it an animal?"
}
```

**Response:**
```json
{
    "answer": "yes"
}
```

**Possible Answers:**
- `"yes"` - The answer is affirmative
- `"no"` - The answer is negative
- `"unclear"` - The AI cannot determine the answer
- `"You won!"` - Correct guess
- `"You lose!"` - 21 questions exceeded
- `"The word I thought of is 'word'."` - Word revealed

## Game Rules

### Question Types
1. **Regular Questions**: "Is it alive?", "Can you eat it?"
2. **Guess Attempts**: "dog", "is it a dog?", "is the word elephant?"
3. **Reveal Commands**: "reveal", "what is the word?", "tell me the word"

### Winning Conditions
- **Win**: Guess the correct word within 21 questions
- **Lose**: Exceed 21 questions without guessing correctly
- **Reveal**: Use a reveal command to see the answer (ends game)

### Supported Guess Formats
- Direct word: `"dog"`
- Question format: `"is it dog"`
- Formal question: `"is the word dog"`
- Article forms: `"is it a dog"`, `"is it an elephant"`

## Testing

### Test Bedrock Connection
Run the test file to verify AWS Bedrock connectivity:
```bash
python bedrock_test.py
```

### Manual API Testing
Use curl or Postman to test endpoints:

```bash
# Start game
curl -X POST http://localhost:5000/start_game

# Ask question
curl -X POST http://localhost:5000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Is it alive?"}'
```

## Troubleshooting

### Common Issues

1. **AWS Credentials Error**
   - Verify AWS credentials are configured
   - Check IAM permissions for Bedrock access
   - Ensure region is set to `us-east-1`

2. **Bedrock Access Denied**
   - Request access to Claude models in AWS Bedrock console
   - Verify IAM policy includes `bedrock:InvokeModel`

3. **Import Errors**
   - Ensure virtual environment is activated
   - Reinstall requirements: `pip install -r requirements.txt`

4. **Port Already in Use**
   - Change port in `main.py`: `app.run(port=5001)`
   - Or kill process using port 5000

### Debug Mode
For development, enable debug mode in `main.py`:
```python
app.run(host="0.0.0.0", port=5000, debug=True)
```

## File Structure
```
twentyonebe/
├── main.py              # Main Flask application
├── bedrock_test.py      # AWS Bedrock connection test
├── requirements.txt     # Python dependencies
├── INSTRUCTIONS.md      # This file
└── venv/               # Virtual environment (created after setup)
```

## Security Notes

- Never commit AWS credentials to version control
- Use environment variables or IAM roles for production
- Disable debug mode in production
- Consider rate limiting for public deployments

## Customization

### Modify Game Parameters
In `main.py`, you can adjust:
- `MAX_QUESTIONS = 21` - Change question limit
- Model temperature and parameters in Bedrock calls
- Add new guess patterns in `is_correct_guess()`

### Add New Features
- Question history tracking
- Multiple game modes
- Difficulty levels
- Score system

## Support

For issues or questions:
1. Check AWS Bedrock service status
2. Verify IAM permissions
3. Review application logs
4. Test with `bedrock_test.py`

## License

[Add your license information here]
