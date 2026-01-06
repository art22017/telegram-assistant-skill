# Telegram Assistant Skill (Extended)

This repository is a technical fork of BayramAnnakov/telegram-assistant-skill, providing advanced automation capabilities for Telegram via MTProto and MCP.

## Technical Enhancements
- Global search functionality across all dialogs.
- Date-based message extraction from Saved Messages (ignores read status).
- Persistent MTProto session management via Telethon.
- Structured JSON output for downstream agent processing.

## Prerequisites
- Python 3.10+
- Telegram API Credentials (API_ID, API_HASH)
- Telethon library
- Configured [telegram-mcp](https://github.com/chigwell/telegram-mcp) server (for workflow integration)

## Configuration

1. **API Credentials**
   Register your application at [my.telegram.org/apps](https://my.telegram.org/apps) to obtain `API_ID` and `API_HASH`.

2. **Environment Setup**
   Copy `env.example` to `.env` and populate the required variables:
   ```env
   TELEGRAM_API_ID=1234567
   TELEGRAM_API_HASH=abcdef0123456789abcdef0123456789
   ```

3. **Dependencies**
   Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Initial Authentication
The client requires a one-time interactive login to generate an encrypted session file.

```bash
python telegram_client.py --auth
```
- Provide your phone number in international format.
- Enter the verification code received via Telegram.
- If enabled, provide your 2FA password.
- A persistent `anon.session` file will be generated in the root directory.

## Core Operations

### Identity Verification
Verify current session status and account metadata:
```bash
python telegram_client.py --whoami
```

### Global Search
Execute a broad search across all accessible dialogs:
```bash
python telegram_client.py --search "query_string"
```

Limit search to a specific chat:
```bash
python telegram_client.py --search "query_string" --chat-id -100123456789
```

### Saved Messages Scraper
Extract historical data from Saved Messages for a specific date (ISO 8601 format):
```bash
python telegram_client.py --scrape-saved 2024-01-15
```

## MCP Workflows
Standardized triggers for AgentSkills.io compliant agents:
- `telegram digest`: Generates summaries of unread communications.
- `analyze writing style`: Extracts linguistic patterns for style matching.
- `post to channel`: Drafts content to channels using extracted styles.

## Security and Persistence
- **Session Persistence**: Subsequent execution reuses the `anon.session` file, bypassing interactive auth.
- **Draft Policy**: All automated messaging defaults to `save_draft` to enforce manual review.
- **Data Privacy**: No telemetry or external logging is implemented. MTProto communication is direct between the client and Telegram servers.

## License
MIT
