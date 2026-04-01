# CommuCraft-AI Setup Guide

Quick setup instructions to get started with the multi-mode learning agent.

## Step 1: Get Your Google API Key

1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable **Generative Language API**
4. Create an API Key in **Credentials** section
5. Copy the key

## Step 2: Configure Environment

Copy the template and edit:
```bash
cp .env.example .env
```

Edit `.env` with your credentials:

**Minimum (Required):**
```
GOOGLE_API_KEY=paste_your_key_here
DAILY_RUN_TIME=14:00
```

**Full Setup (Optional Confluence):**
```
GOOGLE_API_KEY=paste_your_key_here
DAILY_RUN_TIME=14:00

# Confluence integration (optional)
CONFLUENCE_URL=https://your-workspace.atlassian.net/wiki
CONFLUENCE_USERNAME=your.email@company.com
CONFLUENCE_API_TOKEN=your_confluence_token
CONFLUENCE_SPACE=COMMUCRAFT

# Slack notifications (optional)
SLACK_ENABLED=false
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_CHANNEL_ID=C1234567890
```

### Getting Confluence API Token

1. Go to [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click "Create API token"
3. Copy the token and add to `.env`

## Step 3: Set Your Profile

Edit `data/user_profile.json`:
```json
{
  "role": "bioinformatics scientist",
  "proficiency_level": "intermediate",
  "email": "your@email.com"
}
```

**Supported roles:** sales, engineering, marketing, hr, management, bioinformatics scientist, and more

**Supported levels:** beginner, intermediate, advanced

## Step 4: Install Dependencies

```bash
uv sync
```

## Step 5: Choose Your Mode and Run

### Mode 1: Immediate Execution (Testing)

Run immediately and exit:
```bash
uv run commucraft-ai --now
```

This is perfect for testing without waiting for the scheduled time.

### Mode 2: Schedule Mode (Default)

Start background scheduler for daily runs at 2 PM IST:
```bash
# Starts scheduler, doesn't block
uv run commucraft-ai

# Or explicit:
uv run commucraft-ai --schedule
```

The scheduler runs in the background and won't block your CLI. Press Ctrl+C to stop.

### Mode 3: Interactive Chat

Start interactive Q&A with semantic memory:
```bash
uv run commucraft-ai --chat
```

Type your questions, and the agent will answer with memory of previous Q&As. Type "quit" to exit.

## Step 6: Set Up for Automatic Daily Execution

### Option A: Using APScheduler (Recommended)

Just run the scheduler mode in the background:
```bash
nohup uv run commucraft-ai --schedule > logs/scheduler.log 2>&1 &
```

This keeps the scheduler running even after you close the terminal.

### Option B: Using Cron (macOS/Linux)

```bash
crontab -e

# Add this line to run immediate mode at 2 PM daily:
0 14 * * * cd /Users/gowthamkv/my_works/AI_Agent && /usr/local/bin/uv run commucraft-ai --now >> logs/cron.log 2>&1
```

### Option C: Using Task Scheduler (Windows)

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily at 2:00 PM
4. Action: Start program `uv` with arguments: `run commucraft-ai --now`
5. Start in: `C:\path\to\AI_Agent`

## Step 7: Verify It Works

Check the logs:
```bash
tail -f logs/app.log
```

Check generated content:
```bash
ls -la data/daily_content/
cat data/daily_content/2026-04-01.json
```

Run tests to verify setup:
```bash
uv run pytest tests/ -v
```

Expected output:
```
40 passed in 12.33s
```

## Understanding the Three Modes

| Mode | Command | When to Use | Behavior |
|------|---------|-------------|----------|
| **Immediate** | `--now` | Testing, manual runs | Runs immediately, exits |
| **Scheduler** | `--schedule` (default) | Production, automated | Starts background scheduler, runs daily at 2 PM IST |
| **Chat** | `--chat` | Interactive learning | Interactive Q&A with semantic memory |

## File Structure After Setup

```
data/
├── user_profile.json           # Your configuration
└── daily_content/
    ├── 2026-04-01.json        # Today's content
    ├── 2026-03-31.json        # Previous content
    └── ...

logs/
├── app.log                     # Main application logs
└── scheduler.log              # Scheduler logs (if using nohup)

.env                            # Your credentials (keep private!)
```

## Troubleshooting

| Error | Solution |
|-------|----------|
| `GOOGLE_API_KEY not found` | Edit `.env` with your actual key |
| `No module named commucraft_ai` | Run `uv sync` first |
| `Permission denied` (Confluence) | Check your Confluence API token and username |
| `Scheduler didn't start` | Check logs for timezone/permission issues |
| Tests fail | Run `uv run pytest tests/ -v` for details |

## Next Steps

1. **Run the agent:** `uv run commucraft-ai --now` (test mode)
2. **Check logs:** `tail -f logs/app.log`
3. **View content:** `cat data/daily_content/YYYY-MM-DD.json`
4. **Set up daily run:** Use scheduler mode or cron
5. **Try chat mode:** `uv run commucraft-ai --chat`

## What Happens Daily (Scheduler Mode)

1. APScheduler wakes up at 14:00 IST (2 PM)
2. Sends prompt to Google Gemini API
3. Generates paragraph + 10-20 vocabulary words
4. Saves to `data/daily_content/YYYY-MM-DD.json`
5. Appends to Confluence if configured
6. Logs result to `logs/app.log`
7. Returns to waiting for next day

## Support

- Check `logs/app.log` for errors
- Review `README.md` for detailed information
- See `AGENTS.md` for development guidelines
- Check test results: `uv run pytest tests/ -v`
