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

### Default Mode (No Arguments) - Recommended

Generate content immediately and enter interactive chat:
```bash
uv run commucraft-ai
```

The system will:
1. Generate daily learning content right away
2. Save to PDF (always) and Confluence (if configured)
3. Offer interactive chat mode for questions
4. Keep running until you type "quit"

**Perfect for:** Daily interactive learning sessions

### Schedule Mode (`--schedule`)

Start background scheduler for daily runs at 2 PM IST:
```bash
uv run commucraft-ai --schedule
```

The system will:
- Start APScheduler in background (non-blocking)
- Generate content automatically at 2 PM IST each day
- Save to PDF and Confluence (if available)
- Keep running in background (Press Ctrl+C to stop)

**Perfect for:** Automated daily content generation without manual interaction

### Legacy Mode (`--now`)

Generate immediately and exit (for cron jobs):
```bash
uv run commucraft-ai --now
```

The system will:
- Generate content immediately
- Save to PDF and Confluence (if available)
- Exit (suitable for scheduled tasks)

**Perfect for:** Integration with cron or system task schedulers

## Step 6: Storage

**PDF Storage (Always):**
- Primary reliable storage at: `data/pdf_content/YYYY-MM-DD.pdf`
- Always created, regardless of Confluence status
- Includes vocabulary with pronunciation guide
- Fallback formats: HTML (if PDF generation fails)

**JSON Storage:**
- Metadata and detailed vocabulary: `data/daily_content/YYYY-MM-DD.json`
- Used by chat mode and analytics

**Confluence (Optional):**
- If configured, content is also appended to Confluence
- Graceful fallback: PDF works even if Confluence unavailable

## Step 7: Set Up for Automatic Daily Execution

### Option A: Schedule Mode (Recommended)

Start scheduler once (e.g., on login or via systemd):
```bash
nohup uv run commucraft-ai --schedule > logs/scheduler.log 2>&1 &
```

### Option B: Using Cron (macOS/Linux)

```bash
crontab -e

# Add this line to run at 2 PM daily:
0 14 * * * cd /Users/gowthamkv/my_works/AI_Agent && /usr/local/bin/uv run commucraft-ai --now >> logs/cron.log 2>&1
```

### Option C: Using Task Scheduler (Windows)

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily at 2:00 PM
4. Action: Start program `uv` with arguments: `run commucraft-ai --now`
5. Start in: `C:\path\to\AI_Agent`

## Step 8: Verify It Works

Check the logs:
```bash
tail -f logs/app.log
```

Check generated PDF content:
```bash
ls -la data/pdf_content/
open data/pdf_content/2026-04-01.pdf  # macOS
# or on Linux:
xdg-open data/pdf_content/2026-04-01.pdf
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

| Mode | Command | Best For | Saves To |
|------|---------|----------|----------|
| **Default** | (no args) | Interactive learning | PDF + Confluence |
| **Schedule** | `--schedule` | Automated daily runs | PDF + Confluence |
| **Legacy** | `--now` | Cron integration | PDF + Confluence |

## File Structure After Setup

```
data/
├── user_profile.json           # Your configuration
├── daily_content/              # JSON metadata
│   └── 2026-04-01.json        # Generated content
└── pdf_content/               # PDF files (primary)
    └── 2026-04-01.pdf        # Today's PDF

logs/
├── app.log                     # Main application logs
└── scheduler.log              # Scheduler logs (if using nohup)

.env                            # Your credentials (KEEP PRIVATE!)
```

## Troubleshooting

| Error | Solution |
|-------|----------|
| `GOOGLE_API_KEY not found` | Edit `.env` with your actual key |
| `No module named commucraft_ai` | Run `uv sync` first |
| `Permission denied` (Confluence) | Check API token and username, or rely on PDF |
| `PDF not created` | Check `data/pdf_content/` directory exists, or check HTML fallback |
| Tests fail | Run `uv run pytest tests/ -v` for details |

## What Happens in Default Mode

1. Immediately generates learning content
2. Saves to PDF (always)
3. Attempts to save to Confluence (if configured)
4. Displays content to user
5. Offers interactive Q&A with semantic memory
6. Saves Q&As to Confluence (if user chooses and configured)
7. Stays running until user types "quit"

## What Happens in Schedule Mode

1. Starts background scheduler
2. Waits until 14:00 IST (2 PM)
3. Generates learning content
4. Saves to PDF and Confluence (if available)
5. Returns to waiting for next day
6. Repeats daily

## Next Steps

1. **Run default mode:** `uv run commucraft-ai` (try interactive chat)
2. **Check logs:** `tail -f logs/app.log`
3. **View PDF:** `open data/pdf_content/YYYY-MM-DD.pdf` (macOS)
4. **Run tests:** `uv run pytest tests/ -v`
5. **Set up daily:** Use `--schedule` mode or cron

## Support

- Check `logs/app.log` for detailed error information
- Review `README.md` for comprehensive documentation
- See `AGENTS.md` for development guidelines
- Check test results: `uv run pytest tests/ -v`
