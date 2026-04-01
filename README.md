# CommuCraft-AI

A minimal AI-powered daily communication learning system that leverages Google Gemini API and LangChain to help employees continuously improve their professional vocabulary and communication skills.

## Features

- **Three Operational Modes**:
  - `--now`: Generate content immediately and exit (for testing)
  - `--schedule`: Background scheduler runs daily at 2 PM IST (default mode)
  - `--chat`: Interactive Q&A with semantic memory to avoid repetition
- **Daily Learning Content**: Automatically generates professional paragraph tailored to role/level
- **Vocabulary Building**: Creates 10-20 new words with meanings, examples, and phonetic guides
- **Semantic Memory System**: Uses sentence-transformers to find similar Q&As and avoid repetition
- **Confluence Integration**: Saves daily content and chat Q&As to Confluence for team access
- **Customizable**: Supports different roles and proficiency levels (Beginner, Intermediate, Advanced)
- **Progressive Learning**: Vocabulary set slightly above current level to encourage growth
- **JSON Storage**: Daily content stored as JSON for easy access and archival
- **Non-blocking Scheduler**: Runs in background without preventing CLI usage
- **Robust Retry Logic**: Exponential backoff retry mechanism for API resilience
- **Comprehensive Logging**: File-based logging for debugging and monitoring

## Project Structure

```
CommuCraft-AI/
├── src/
│   └── commucraft_ai/
│       ├── __init__.py
│       ├── main.py                           # Three-mode entry point
│       ├── config.py                         # Config management with Confluence
│       ├── agent/
│       │   ├── __init__.py
│       │   ├── daily_learning_agent.py      # LangChain Gemini agent
│       │   └── query_agent.py               # Query agent with semantic memory
│       ├── prompts/
│       │   ├── __init__.py
│       │   └── daily_learning.py            # Prompt templates
│       ├── storage/
│       │   ├── __init__.py
│       │   ├── daily_storage.py             # JSON persistence
│       │   ├── confluence_storage.py        # Confluence API wrapper
│       │   └── memory_system.py             # Semantic memory search
│       └── utils/
│           ├── __init__.py
│           ├── logger.py                    # File-based logging
│           ├── retry_handler.py             # Exponential backoff retry
│           ├── markdown_formatter.py        # Markdown formatting
│           └── slack_messenger.py           # Optional Slack integration
├── data/
│   ├── user_profile.json                    # User configuration
│   └── daily_content/                       # Generated daily content
├── logs/
│   └── app.log                              # Application logs
├── tests/
│   ├── test_daily_agent.py                 # Agent tests (7 tests)
│   ├── test_markdown_formatter.py          # Formatter tests (16 tests)
│   └── test_storage.py                     # Storage tests (17 tests)
├── .env                                     # Environment variables
├── .env.example                             # Environment template
├── pyproject.toml                           # Project config & dependencies
├── AGENTS.md                                # Development guidelines
├── SETUP.md                                 # Setup instructions
└── README.md                                # This file
```

## Quick Start

### Prerequisites

- Python 3.9 or higher
- `uv` package manager ([install uv](https://docs.astral.sh/uv/))
- Google API key with Gemini access
- Confluence workspace (optional, for memory and content sharing)

### Setup

1. **Clone the repository** (if not already done)
   ```bash
   cd /Users/gowthamkv/my_works/AI_Agent
   ```

2. **Create and populate `.env` file**
   ```bash
   # Copy the template
   cp .env.example .env
   ```
   
   Edit `.env` with your credentials:
   ```
   GOOGLE_API_KEY=your_actual_google_api_key_here
   DAILY_RUN_TIME=14:00
   
   # Optional: Confluence integration for memory
   CONFLUENCE_URL=https://your-workspace.atlassian.net/wiki
   CONFLUENCE_USERNAME=your.email@company.com
   CONFLUENCE_API_TOKEN=your_confluence_api_token
   CONFLUENCE_SPACE=COMMUCRAFT
   
   # Optional: Slack notifications
   SLACK_ENABLED=false
   SLACK_BOT_TOKEN=your_slack_token
   SLACK_CHANNEL_ID=C1234567890
   ```

3. **Update user profile** (`data/user_profile.json`)
   ```json
   {
     "role": "bioinformatics scientist",
     "proficiency_level": "intermediate",
     "email": "your.email@company.com"
   }
   ```
   
   Supported roles: `sales`, `engineering`, `marketing`, `hr`, `management`, `bioinformatics scientist`, etc.
   
   Supported levels: `beginner`, `intermediate`, `advanced`

4. **Install dependencies**
   ```bash
   uv sync
   ```

### Running the Agent

#### Mode 1: Immediate Execution (`--now`)

Generate content immediately and exit. Perfect for testing:

```bash
uv run commucraft-ai --now
```

The agent will:
1. Load configuration
2. Initialize Gemini LLM
3. Generate daily learning content immediately
4. Save to `data/daily_content/YYYY-MM-DD.json`
5. Append to Confluence if configured
6. Exit

**Output:**
```
[INFO] Running in immediate mode (--now)
[INFO] Generating content for role: bioinformatics scientist, level: intermediate
[INFO] ✓ Daily content successfully generated and saved
[INFO] ✓ Generated 14 vocabulary words
[INFO] ✓ Content appended to Confluence
[INFO] ✓ Immediate run completed successfully. Exiting.
```

#### Mode 2: Schedule Mode (`--schedule`)

Start background scheduler for daily runs at 2 PM IST. This is the **default mode**:

```bash
# Default: starts scheduler
uv run commucraft-ai

# Or explicit:
uv run commucraft-ai --schedule
```

The agent will:
1. Initialize Gemini LLM and Confluence storage
2. Start APScheduler in background (IST timezone)
3. Run daily job at 14:00 (2 PM) IST
4. Keep running until you press Ctrl+C
5. Does NOT block - you can use the CLI afterwards

**Output:**
```
[INFO] Running in schedule mode (--schedule)
[INFO] Setting up APScheduler...
[INFO] ✓ Scheduler started. Next run: 2026-04-02 14:00:00+05:30
[INFO] Scheduler is running. Press Ctrl+C to stop.
```

#### Mode 3: Interactive Chat Mode (`--chat`)

Start interactive Q&A with semantic memory:

```bash
uv run commucraft-ai --chat
```

The agent will:
1. Load Confluence storage and semantic memory system
2. Start interactive chat loop
3. Answer your questions with AI assistance
4. Remember previous Q&As to avoid repetition
5. Optionally save Q&As to Confluence

**Example Session:**
```
[INFO] ✓ Chat mode started. Type your questions (type 'quit' to stop)
────────────────────────────────────────────────────────────────

You: What is bioinformatics?
Agent: Bioinformatics is an interdisciplinary field that applies computational...
────────────────────────────────────────────────────────────────

Save this Q&A? (yes/no): yes
✓ Q&A saved to Confluence

You: quit
```

#### Schedule with System Task Scheduler

For automatic daily runs without needing to keep a terminal open:

**macOS/Linux (Cron):**
```bash
# Edit crontab
crontab -e

# Add this line to run at 2 PM daily:
0 14 * * * cd /Users/gowthamkv/my_works/AI_Agent && /usr/local/bin/uv run commucraft-ai --now >> logs/cron.log 2>&1
```

**Windows (Task Scheduler):**
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger to daily at 2:00 PM
4. Set action: Run `uv run commucraft-ai --now` in project directory

## Configuration

### Environment Variables (`.env`)

Required:
```
GOOGLE_API_KEY=your_google_api_key_here    # Required: Google Gemini API key
DAILY_RUN_TIME=14:00                       # When to run (24-hour format, IST)
```

Optional - Confluence Integration:
```
CONFLUENCE_URL=https://your-workspace.atlassian.net/wiki
CONFLUENCE_USERNAME=your.email@company.com
CONFLUENCE_API_TOKEN=your_api_token
CONFLUENCE_SPACE=COMMUCRAFT
```

Optional - Slack Notifications:
```
SLACK_ENABLED=false
SLACK_BOT_TOKEN=xoxb-...
SLACK_CHANNEL_ID=C1234567890
```

### User Profile (`data/user_profile.json`)

```json
{
  "role": "bioinformatics scientist",    # Your job role
  "proficiency_level": "intermediate",   # beginner, intermediate, or advanced
  "email": "user@company.com"            # Email (optional)
}
```

### Confluence Pages

When Confluence is configured, the system creates/uses:
- **CommuCraft Daily Learning Content**: Appends daily generated content
- **CommuCraft Chat Q&A Memory**: Stores user-saved Q&As (chat mode)

## Generated Content Format

Daily content is saved as JSON files in `data/daily_content/YYYY-MM-DD.json`:

```json
{
  "date": "2026-04-01",
  "role": "bioinformatics scientist",
  "proficiency_level": "intermediate",
  "intro_message": "Today's Learning Focus: ...",
  "paragraph": "Building strong client relationships requires clear and persuasive communication...",
  "vocabulary": [
    {
      "word": "proteome",
      "meaning": "The complete set of proteins expressed by a genome",
      "usage_example": "The proteome analysis revealed significant changes in protein expression levels.",
      "phonetic": "PROW-tee-ohm"
    },
    {
      "word": "sequencing",
      "meaning": "Determining the order of nucleotides in DNA or RNA",
      "usage_example": "DNA sequencing is fundamental to modern bioinformatics research.",
      "phonetic": "SEE-kwen-sing"
    }
    // ... more words (10-20 total)
  ]
}
```

## Semantic Memory System

The chat mode uses sentence-transformers (MiniLM-L6-v2) to find similar questions from your previous Q&As before answering. This prevents repetitive answers and provides context-aware responses.

**How it works:**
1. User asks a question
2. System searches previous Q&As for semantic similarity (threshold: 0.5)
3. If similar Q&As found, includes them as context for the LLM
4. LLM generates answer aware of previous responses
5. System saves Q&A only if user explicitly says "yes"

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

### Three Modes

**Mode 1: Immediate (`--now`)**
- Run once and exit
- Useful for testing or manual daily run
- Does not require scheduling infrastructure

**Mode 2: Scheduler (`--schedule` or default)**
- Runs in background using APScheduler
- Non-blocking: doesn't prevent CLI usage
- Uses IST timezone for scheduling
- Daily job runs at 2 PM IST

**Mode 3: Interactive Chat (`--chat`)**
- Interactive Q&A with semantic memory
- Uses QueryAgent with ConfluenceStorage
- Searches previous responses before answering
- Saves Q&As optionally to Confluence

### LangChain Agent
- **Type**: Simple prompt chain (for daily generation)
- **LLM**: Google Gemini (`gemini-pro` via langchain-google-genai)
- **Pattern**: System prompt + User prompt → LLM → JSON response

### Semantic Memory
- **Library**: sentence-transformers (MiniLM-L6-v2)
- **Purpose**: Find similar Q&As to avoid repetition
- **Threshold**: 0.5 (configurable)
- **Returns**: Top 3 similar responses by default

### Confluence Integration
- **Library**: atlassian-python-api
- **Purpose**: Persistent storage and team sharing
- **Pages**: Separate docs for daily content and chat Q&As
- **Graceful Degradation**: Works without Confluence (optional)

### Retry Logic
- **Mechanism**: Exponential backoff decorator
- **Attempts**: Max 3 retries with delays of 1s, 2s, 4s
- **Failure Handling**: Logs all attempts and raises exception after max retries

### Storage
- **Format**: JSON files per date (`YYYY-MM-DD.json`)
- **Validation**: Schema validation before saving
- **Overwrite**: Regenerates if same date runs multiple times
- **Confluence**: Appends with timestamps (non-destructive)

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
- **langchain-google-genai** (>=2.0.0) - LangChain integration for Gemini
- **google-genai** (>=0.5.0) - Google Gemini API client (new package)
- **apscheduler** (>=3.10.0) - Background task scheduling
- **python-dotenv** (>=1.0.0) - Environment variable management
- **atlassian-python-api** (>=3.41.0) - Confluence API integration
- **sentence-transformers** (>=2.2.2) - Semantic similarity search

### Development
- **pytest** (>=8.0) - Testing framework
- **ruff** (>=0.1.0) - Code linting and formatting

**Note:** We migrated from deprecated `google.generativeai` to `google-genai` package. The system still uses `langchain-google-genai` which wraps the old package internally, but we recommend monitoring for full migration.

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

### Scheduler doesn't start
1. Verify configuration loaded correctly
2. Check logs for APScheduler errors
3. Ensure timezone "Asia/Kolkata" is available on your system

### Confluence permission errors
The system gracefully degrades when Confluence is not configured or accessible:
- Daily content still saves to JSON
- Chat mode works without Confluence
- No Q&As saved if Confluence unavailable
- Check logs for specific permission issues

### Chat mode not saving Q&As
1. Verify Confluence is configured in `.env`
2. Check CONFLUENCE_USERNAME and CONFLUENCE_API_TOKEN
3. Ensure Confluence user has permission to create pages
4. Check logs for specific errors

### Tests fail with import errors
Ensure pytest is using the correct pythonpath:
```bash
uv run pytest tests/ -v
```

### All 40 tests passing but scheduler mode won't start
Check if port 5000 or other scheduler ports are blocked by firewall. APScheduler uses IPC mechanisms that might require port access.

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
