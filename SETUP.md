# CommuCraft-AI Setup Guide

Quick setup instructions to get started with the daily learning agent.

## Step 1: Get Your Google API Key

1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable **Generative Language API**
4. Create an API Key in **Credentials** section
5. Copy the key

## Step 2: Configure Environment

```bash
# Edit .env file with your API key
# Open .env and replace placeholder:
GOOGLE_API_KEY=paste_your_key_here
DAILY_RUN_TIME=09:00  # Set your preferred time
```

## Step 3: Set Your Profile

Edit `data/user_profile.json`:
```json
{
  "role": "sales",              # Change to your role
  "proficiency_level": "intermediate",  # Change to your level
  "email": "your@email.com"     # Optional
}
```

## Step 4: Install Dependencies

```bash
uv sync
```

## Step 5: Run the Agent

```bash
# Run and wait for scheduled time
uv run commucraft-ai

# Or test immediately (ignores DAILY_RUN_TIME)
uv run commucraft-ai --now
```

## Step 6: Schedule Daily Execution

**macOS/Linux - Cron:**
```bash
crontab -e

# Add this line to run at 9 AM daily:
0 9 * * * cd /Users/gowthamkv/my_works/AI_Agent && /usr/local/bin/uv run commucraft-ai >> logs/cron.log 2>&1
```

**Windows - Task Scheduler:**
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily at 9:00 AM
4. Action: Start program `uv` with arguments: `run commucraft-ai`
5. Start in: `C:\path\to\AI_Agent`

## Verify It Works

Check the logs:
```bash
tail -f logs/app.log
```

Check generated content:
```bash
ls -la data/daily_content/
cat data/daily_content/2026-03-24.json
```

## Test Runs

Run tests to verify setup:
```bash
uv run pytest tests/ -v
```

## Troubleshooting

| Error | Solution |
|-------|----------|
| `GOOGLE_API_KEY not found` | Edit `.env` with your actual key |
| `No module named commucraft_ai` | Run `uv sync` first |
| Agent doesn't run | Check `DAILY_RUN_TIME` format is `HH:MM` |

## What Happens Daily

1. Agent starts and loads configuration
2. Waits until `DAILY_RUN_TIME`
3. Sends prompt to Google Gemini API
4. Generates paragraph + 10-20 vocabulary words
5. Saves to `data/daily_content/YYYY-MM-DD.json`
6. Logs result to `logs/app.log`
7. Exits

## File Structure

```
data/
├── user_profile.json           # Your configuration
└── daily_content/
    ├── 2026-03-24.json        # Today's content
    ├── 2026-03-23.json        # Yesterday's content
    └── ...

logs/
└── app.log                     # All logs here

.env                            # Your API key (KEEP PRIVATE!)
```

## Next Steps

1. Run the agent: `uv run python -m commucraft_ai.main`
2. Check logs: `tail -f logs/app.log`
3. View generated content: `cat data/daily_content/YYYY-MM-DD.json`
4. Set up cron job for automatic daily execution
5. Monitor logs regularly

## Support

- Check `logs/app.log` for errors
- Review `README.md` for detailed information
- See `AGENTS.md` for development guidelines
