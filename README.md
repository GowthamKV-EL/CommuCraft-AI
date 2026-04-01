# CommuCraft-AI

A minimal AI-powered daily communication learning system that leverages Google Gemini API and LangChain to help employees continuously improve their professional vocabulary and communication skills.

## Features

- **Daily Learning Content**: Automatically generates one professional paragraph daily tailored to user's role and proficiency level
- **Vocabulary Building**: Creates 10-20 new words with meanings, usage examples, and phonetic pronunciation guides
- **Customizable**: Supports different job roles (Sales, Engineering, Marketing, etc.) and proficiency levels (Beginner, Intermediate, Advanced)
- **Progressive Learning**: Vocabulary is set slightly above current level to encourage growth
- **JSON Storage**: Daily content is stored as JSON for easy access and archival
- **Automatic Scheduling**: Uses APScheduler to run daily at specified time
- **Robust Retry Logic**: Exponential backoff retry mechanism for API resilience
- **Comprehensive Logging**: File-based logging for debugging and monitoring

## Project Structure

```
CommuCraft-AI/
├── src/
│   └── commucraft_ai/
│       ├── __init__.py
│       ├── main.py                           # Entry point with APScheduler
│       ├── config.py                         # Config management
│       ├── agent/
│       │   ├── __init__.py
│       │   └── daily_learning_agent.py      # LangChain Gemini agent
│       ├── prompts/
│       │   ├── __init__.py
│       │   └── daily_learning.py            # Prompt templates
│       ├── storage/
│       │   ├── __init__.py
│       │   └── daily_storage.py             # JSON persistence
│       └── utils/
│           ├── __init__.py
│           ├── logger.py                    # File-based logging
│           └── retry_handler.py             # Exponential backoff retry
├── data/
│   ├── user_profile.json                    # User configuration
│   └── daily_content/                       # Generated daily content
├── logs/
│   └── app.log                              # Application logs
├── tests/
│   ├── __init__.py
│   ├── test_daily_agent.py                 # Agent tests
│   └── test_storage.py                     # Storage tests
├── .env                                     # Environment variables
├── pyproject.toml                           # Project config & dependencies
├── AGENTS.md                                # Development guidelines
└── README.md                                # This file
```

## Quick Start

### Prerequisites

- Python 3.9 or higher
- `uv` package manager ([install uv](https://docs.astral.sh/uv/))
- Google API key with Gemini access

### Setup

1. **Clone the repository** (if not already done)
   ```bash
   cd /Users/gowthamkv/my_works/AI_Agent
   ```

2. **Create and populate `.env` file**
   ```bash
   # Copy the template and add your Google API key
   cat .env  # Already created with placeholder
   ```
   
   Edit `.env` with your actual Google API key:
   ```
   GOOGLE_API_KEY=your_actual_google_api_key_here
   DAILY_RUN_TIME=09:00
   ```

3. **Update user profile** (`data/user_profile.json`)
   ```json
   {
     "role": "sales",              # Your job role
     "proficiency_level": "intermediate",  # Your language level
     "email": "your.email@company.com"     # Your email (optional)
   }
   ```
   
   Supported roles: `sales`, `engineering`, `marketing`, `hr`, `management`, etc.
   
   Supported levels: `beginner`, `intermediate`, `advanced`

4. **Install dependencies**
   ```bash
   uv sync
   ```

### Running the Agent

#### Standard Execution
The agent runs and waits until the scheduled time, then executes the job:

```bash
commucraft-ai
```

Or with `uv run`:

```bash
uv run commucraft-ai
```

**Important:** The agent will **block and wait** until the scheduled time (from `DAILY_RUN_TIME` in `.env`) before generating content. For example, if `DAILY_RUN_TIME=09:00` and you run the command at 8:00 AM, it will wait until 9:00 AM.

#### Test Immediately
To run immediately without waiting for the scheduled time:

```bash
commucraft-ai --now
```

Or with `uv run`:

```bash
uv run commucraft-ai --now
```

The agent will:
1. Load your configuration
2. Initialize the Gemini LLM  
3. Generate daily learning content immediately (ignores `DAILY_RUN_TIME`)
4. Save to `data/daily_content/YYYY-MM-DD.json`
5. Exit

#### Schedule with System Task Scheduler

**macOS (Cron):**
```bash
# Edit crontab
crontab -e

# Add this line to run at 9:00 AM daily
0 9 * * * cd /Users/gowthamkv/my_works/AI_Agent && /usr/local/bin/uv run commucraft-ai
```

**Linux (Cron):**
```bash
crontab -e

# Add this line
0 9 * * * cd /path/to/AI_Agent && uv run commucraft-ai
```

**Windows (Task Scheduler):**
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger to daily at 9:00 AM
4. Set action: Run `uv run commucraft-ai` in your project directory

## Configuration

### Environment Variables (`.env`)

```
GOOGLE_API_KEY=your_google_api_key_here    # Required: Google Gemini API key
DAILY_RUN_TIME=09:00                       # When to run daily (24-hour format)
```

### User Profile (`data/user_profile.json`)

```json
{
  "role": "sales",                    # Job role
  "proficiency_level": "intermediate", # Language level
  "email": "user@company.com"        # Email (optional)
}
```

## Generated Content Format

Daily content is saved as JSON files in `data/daily_content/YYYY-MM-DD.json`:

```json
{
  "date": "2026-03-24",
  "role": "sales",
  "proficiency_level": "intermediate",
  "paragraph": "Building strong client relationships requires clear and persuasive communication...",
  "vocabulary": [
    {
      "word": "articulate",
      "meaning": "To express ideas clearly and effectively",
      "usage_example": "The sales director articulated the new strategy during the meeting.",
      "pronunciation": "ar-TIK-yuh-layt"
    },
    {
      "word": "conviction",
      "meaning": "A strong belief or firm opinion",
      "usage_example": "She spoke with conviction about the product benefits.",
      "pronunciation": "kun-VIK-shun"
    }
    // ... more words (10-20 total)
  ]
}
```

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_daily_agent.py -v

# Run with coverage
uv run pytest --cov=src tests/
```

### Code Quality

```bash
# Format code
uv run ruff format .

# Check linting issues
uv run ruff check .

# Fix auto-fixable issues
uv run ruff check --fix .
```

All code follows the guidelines in [AGENTS.md](./AGENTS.md):
- 120-character line length limit
- Complete type hints on all functions
- Comprehensive docstrings with Args, Returns, and Errors sections
- No `Any` type unless absolutely necessary

## Architecture

### LangChain Agent
- **Type**: Simple prompt chain (no complex tools needed for daily generation)
- **LLM**: Google Gemini (`gemini-pro`)
- **Pattern**: System prompt + User prompt → LLM → JSON response

### Retry Logic
- **Mechanism**: Exponential backoff decorator
- **Attempts**: Max 3 retries with delays of 1s, 2s, 4s
- **Failure Handling**: Logs all attempts and raises exception after max retries

### Storage
- **Format**: JSON files per date (`YYYY-MM-DD.json`)
- **Validation**: Schema validation before saving
- **Overwrite**: Regenerates if same date runs multiple times

### Scheduling
- **Tool**: APScheduler (BackgroundScheduler)
- **Trigger**: Cron expression (daily at specified time)
- **Execution**: Runs once per program execution, then exits

## Error Handling & Escalation

| Issue | Behavior |
|-------|----------|
| Missing GOOGLE_API_KEY | Log error and exit immediately |
| Invalid user_profile.json | Log error and exit immediately |
| API call fails after 3 retries | Log error, skip day (no content generated) |
| Invalid LLM response JSON | Log error, skip day (retry on next run) |
| Directory creation fails | Create parent directories recursively |

## Logging

Logs are saved to `logs/app.log` with the following format:

```
[2026-03-24 09:00:15] [INFO] [commucraft_ai.main] - Starting daily learning job
[2026-03-24 09:00:15] [INFO] [commucraft_ai.config] - Configuration loaded
[2026-03-24 09:00:16] [INFO] [commucraft_ai.agent] - Generating daily content
[2026-03-24 09:00:18] [INFO] [commucraft_ai.storage] - Saved to data/daily_content/2026-03-24.json
```

Log files rotate automatically at 10MB with 5 backup files kept.

## API Key Setup

### Getting a Google API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the **Generative Language API**
4. Go to **Credentials** → **Create Credentials** → **API Key**
5. Copy the API key and add to `.env` file

### Testing Your API Key

```bash
python -c "
from langchain_google_genai import ChatGoogleGenerativeAI
llm = ChatGoogleGenerativeAI(model='gemini-pro', google_api_key='YOUR_KEY')
print(llm.invoke('Hello'))
"
```

## Dependencies

### Core
- **langchain** (>=0.1.0) - LLM orchestration framework
- **google-generativeai** (>=0.3.0) - Google Gemini API client
- **langchain-google-genai** (>=2.0.0) - LangChain integration for Gemini
- **apscheduler** (>=3.10.0) - Task scheduling
- **python-dotenv** (>=1.0.0) - Environment variable management

### Development
- **pytest** (>=7.0) - Testing framework
- **ruff** (>=0.1.0) - Code linting and formatting

## Troubleshooting

### "No module named 'commucraft_ai'"
Ensure `uv sync` has been run and dependencies are installed:
```bash
uv sync
```

### "Cannot find commucraft-ai command"
The CLI entry point needs to be installed. Run:
```bash
uv sync
```

Then verify the command is available:
```bash
uv run commucraft-ai --help
```

### "GOOGLE_API_KEY not found"
Check that `.env` file exists and contains your actual API key (not the placeholder).

### Agent doesn't run at scheduled time
1. Verify `DAILY_RUN_TIME` format is `HH:MM` (e.g., `09:00`)
2. Check system time is correct
3. For cron jobs, verify the full path to `uv` is correct

### Tests fail with import errors
Ensure pytest is using the correct pythonpath:
```bash
uv run pytest tests/ -v
```

## Next Steps

1. **Add message rewriting**: Create a message rewriting tool for professional emails
2. **Add meeting prep**: Add meeting preparation tool with talking points
3. **User feedback**: Collect feedback on daily content quality and adjust prompts
4. **Analytics**: Track user engagement with generated content
5. **Multi-language**: Expand to support multiple languages

## Contributing

Follow the guidelines in [AGENTS.md](./AGENTS.md):
- Use `uv` for dependency management
- Write tests for all new features
- Run `ruff format .` and `ruff check .` before committing
- Ensure all tests pass with `pytest`
- Add comprehensive docstrings to all functions

## License

Internal project for professional communication improvement.

## Support

For issues or questions, check the logs in `logs/app.log` or refer to the [AGENTS.md](./AGENTS.md) development guidelines.
