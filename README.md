# CommuCraft-AI

An AI-powered daily communication improvement system that helps employees enhance their professional communication skills through:

- **Daily Learning**: Automatic daily vocabulary lessons with 10-20 professional words, meanings, and audio pronunciation
- **Message Rewriting**: Intelligent rewriting of emails, chat messages, and documents for clarity and professionalism
- **Meeting Preparation**: Comprehensive preparation guidance for important professional meetings and calls

## Features

### 1. Daily Learning
- Generates daily professional communication insights
- Provides 10-20 vocabulary words tailored to user proficiency level
- Includes meanings and example usage for each word
- Google Text-to-Speech audio pronunciation for all vocabulary
- Automatically scheduled daily at configured time

### 2. Message Rewriting
- Rewrites professional messages while preserving original intent
- Supports multiple communication types: emails, chat, documents, updates, presentations
- Customizable tone: formal, casual, professional, friendly, assertive
- Provides alternative versions and improvement analysis
- Maintains communication history for reference

### 3. Meeting Preparation
- Generates structured talking points for meetings
- Creates professional opening statements
- Identifies potentially challenging questions with suggested responses
- Provides communication tips tailored to audience
- Creates preparation checklist

## Installation

### Prerequisites
- Python 3.9 or higher
- Google Gemini API key
- Google Cloud credentials (for Text-to-Speech)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AI_Agent
   ```

2. **Install dependencies using uv**
   ```bash
   uv sync
   ```

3. **Configure environment variables**
   ```bash
   # Edit .env file with your configuration
   nano .env
   ```
   
   Required variables:
   ```env
   GOOGLE_API_KEY=your_google_gemini_api_key
   DAILY_LEARNING_TIME=09:00
   USER_PROFICIENCY_LEVEL=intermediate
   ```

## Usage

### Running the Application

#### Daemon Mode (with scheduler)
```bash
uv run python main.py
```
This starts the application with the APScheduler, executing daily learning at the configured time.

#### Interactive Mode
```bash
uv run python main.py --interactive
# or
uv run python main.py -i
```
This starts an interactive prompt where you can directly test the agent functions.

### Interactive Commands
In interactive mode, you can:
- Request daily learning: `Generate today's daily learning`
- Rewrite messages: `Help me rewrite this email: [your message]`
- Prepare for meetings: `Prepare me for a meeting with my manager about the Q1 project`
- Check status: `status`
- Get help: `help`
- Exit: `quit`

## Project Structure

```
CommuCraft-AI/
├── src/
│   └── sc_bot/
│       ├── agent/
│       │   └── base_agent.py          # Main LangChain ReAct agent
│       ├── tasks/
│       │   ├── daily_learning.py      # Daily learning generation
│       │   ├── message_rewriter.py    # Message rewriting logic
│       │   └── meeting_prep.py        # Meeting preparation
│       ├── storage/
│       │   └── json_storage.py        # JSON-based persistence
│       ├── utils/
│       │   └── google_tts.py          # Google Text-to-Speech integration
│       ├── config.py                  # Configuration management
│       ├── error_handling.py          # Error handling and validation
│       ├── scheduler.py               # APScheduler integration
│       └── __init__.py
├── tests/
│   ├── test_storage.py                # Storage tests
│   ├── test_error_handling.py         # Error handling tests
│   ├── test_scheduler.py              # Scheduler tests
│   └── conftest.py                    # Pytest configuration
├── main.py                            # Application entry point
├── .env                               # Environment variables
├── pyproject.toml                     # Project configuration
├── AGENTS.md                          # Agent guidelines
└── README.md                          # This file
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GOOGLE_API_KEY` | Required | Google Gemini API key |
| `DAILY_LEARNING_TIME` | 09:00 | Time to run daily learning (HH:MM format) |
| `USER_PROFICIENCY_LEVEL` | intermediate | User's English proficiency (beginner/intermediate/advanced) |
| `USER_ROLE_FOCUS` | general | User's role or domain focus |
| `TTS_LANGUAGE_CODE` | en-US | Language code for Text-to-Speech |
| `TTS_VOICE_NAME` | en-US-Neural2-A | Voice name for Text-to-Speech |
| `DATA_DIR` | ./data | Directory for storing data |
| `LOG_LEVEL` | INFO | Logging level |
| `DEBUG` | False | Debug mode |

## API Components

### CommuCraftAgent
The main AI agent using LangChain's ReAct pattern with Google Gemini.

**Methods:**
- `run(user_input: str) -> str`: Execute agent with user input
- `shutdown()`: Gracefully shutdown the agent

### DailyLearningTask
Generates daily learning content.

**Methods:**
- `generate_daily_content() -> dict`: Generate daily learning
- `get_today_learning() -> Optional[dict]`: Retrieve today's content

### MessageRewriterTask
Rewrites professional messages.

**Methods:**
- `rewrite_message(...) -> dict`: Rewrite a message with analysis
- `get_communication_history(user_id, limit=10) -> list`: Get history

### MeetingPrepTask
Prepares for meetings and calls.

**Methods:**
- `prepare_meeting(...) -> dict`: Generate meeting preparation
- `_generate_talking_points(...)`: Generate discussion talking points
- `_identify_challenging_questions(...)`: Anticipate difficult questions

### TaskScheduler
Manages scheduled task execution.

**Methods:**
- `add_daily_job(job_id, func, time)`: Add daily scheduled job
- `add_cron_job(job_id, func, cron_schedule)`: Add cron scheduled job
- `start()`: Start the scheduler
- `stop()`: Stop the scheduler
- `list_jobs() -> list`: List all scheduled jobs

### JSONStorage
Persistent data storage using JSON files.

**Methods:**
- `save_daily_learning(content)`: Save daily learning content
- `load_daily_learning(date_str)`: Load daily learning
- `save_user_profile(user_id, profile)`: Save user profile
- `load_user_profile(user_id)`: Load user profile
- `save_communication_history(user_id, entry)`: Save message rewrite
- `load_communication_history(user_id, limit)`: Load rewrite history
- `save_meeting_prep(user_id, prep_data)`: Save meeting preparation
- `list_files(pattern)`: List stored files

## Testing

### Run all tests
```bash
uv run pytest
```

### Run specific test file
```bash
uv run pytest tests/test_storage.py -v
```

### Run with coverage
```bash
uv run pytest tests/ --cov=src/sc_bot
```

## Code Quality

### Linting and Formatting
```bash
# Check code style
uv run ruff check src/ tests/ main.py

# Fix auto-fixable issues
uv run ruff check --fix src/ tests/ main.py

# Format code
uv run ruff format src/ tests/ main.py
```

### Pre-commit Workflow
1. Run: `uv run ruff check --fix .`
2. Format: `uv run ruff format .`
3. Test: `uv run pytest`
4. Commit changes

## Error Handling

The system includes comprehensive error handling and escalation:

- **ValidationError**: Input validation failures
- **StorageError**: Data persistence failures
- **LLMError**: API call failures
- **EscalationRequiredError**: Unclear user intent requiring clarification

### Escalation Levels
- `CLARIFICATION_NEEDED`: User needs to provide more details
- `INTENT_AMBIGUOUS`: Request could be interpreted multiple ways
- `INSUFFICIENT_CONTEXT`: Missing background information
- `INVALID_REQUEST`: Request format is invalid

## Data Storage

All data is stored locally in JSON format in the `./data` directory:

- `daily_learning_YYYY-MM-DD.json`: Daily learning content
- `user_profiles.json`: User configuration and preferences
- `communication_history_[user_id].json`: Message rewriting history
- `meeting_prep_[user_id].json`: Meeting preparation records
- `audio/`: Audio pronunciation files for vocabulary

## Logging

Logs are written to:
- Console output: Real-time application events
- `commucraft.log`: Persistent log file with full details

## Dependencies

### Core Dependencies
- **langchain**: AI agent framework
- **google-generativeai**: Google Gemini API access
- **google-cloud-texttospeech**: Audio synthesis for pronunciation
- **apscheduler**: Task scheduling
- **pydantic**: Data validation
- **python-dotenv**: Environment management

### Development Dependencies
- **pytest**: Testing framework
- **ruff**: Linting and formatting

## Troubleshooting

### Missing API Key
**Error**: `GOOGLE_API_KEY not found in environment`
**Solution**: Add your Google Gemini API key to `.env` file

### Permission Denied on Data Directory
**Error**: `PermissionError: [Errno 13] Permission denied: './data'`
**Solution**: Ensure the application has write permissions to the current directory

### Scheduler Not Running
**Error**: Jobs not executing at scheduled time
**Solution**: 
- Ensure the application is running continuously
- Check that `DAILY_LEARNING_TIME` is in valid HH:MM format
- Verify logs for any errors

### Tests Failing
**Solution**: 
```bash
uv sync  # Ensure dependencies are up to date
uv run pytest tests/ -v  # Run with verbose output
```

## Contributing

Please follow the guidelines in `AGENTS.md`:
- Use `uv` for package management
- Follow PEP 8 with 120-character line limit
- Use complete type hints in all functions
- Write comprehensive docstrings
- Run tests before committing

## License

[Your License Here]

## Support

For issues, questions, or feature requests, please open an issue in the repository.

---

**Last Updated**: March 23, 2026
**Version**: 0.1.0
