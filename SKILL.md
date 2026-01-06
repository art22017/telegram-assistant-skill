---
name: telegram-assistant
description: |
  Advanced Telegram automation assistant using telegram-mcp and local Telethon client. Use when users want to:
  (1) Get a digest of unread Telegram messages
  (2) Analyze their writing style from channel posts
  (3) Draft and publish posts to Telegram channels
  (4) Search and reply to messages across chats
  (5) Deep search across all chats with keywords
  (6) Scrape "Saved Messages" by specific date
  Triggers: "telegram digest", "unread messages", "summary",
  "post to channel", "draft telegram post", "analyze writing style",
  "extract style from channel", "search telegram", "find in telegram",
  "scrape saved messages", "telegram search", "telegram workflow"
license: MIT
compatibility: |
  Requires:
  - telegram-mcp server configured in the MCP client (for digest and posting workflows).
  - telegram_client.py (for advanced search and scraping, uses Telethon directly).
metadata:
  author: Bayram Annakov (onsa.ai), Extended by Community
  version: "2.0.0"
  category: productivity
  telegram-mcp-repo: https://github.com/chigwell/telegram-mcp
  telethon-repo: https://github.com/LonamiWebs/Telethon
allowed-tools: mcp__telegram-mcp__* Read Write Edit Glob Bash
---

# Telegram Assistant

Automate Telegram workflows: digests, channel posting, style-matched drafts, and advanced search/scraping.

## Quick Start Reference

- Morning digest: Use Digest Workflow (via telegram-mcp).
- Channel posting: Use Style + Post Workflow.
- Search all chats: Use Search Workflow (via telegram_client.py).
- Scrape Saved Messages by date: Use Scrape Workflow.
- Replying to messages: Use Reply Workflow.

---

## Authentication

Authentication is required for search and scrape features.

```bash
cd telegram
pip install -r requirements.txt
export TELEGRAM_API_ID=your_api_id
export TELEGRAM_API_HASH=your_api_hash
python telegram_client.py --auth
```

---

## Workflow 0: Search

Goal: Search across all chats or a specific chat for messages containing keywords.

### CLI Usage

```bash
# Global search
python telegram_client.py --search "keyword"

# Specific chat search
python telegram_client.py --search "keyword" --chat-id 123456789
```

### Integration
When a user requests a search, call `python telegram_client.py --search "query"`, parse the JSON output, and present the results.

---

## Workflow 1: Scrape Saved Messages

Goal: Extract all messages from "Saved Messages" for a specific date (YYYY-MM-DD).

### CLI Usage

```bash
python telegram_client.py --scrape-saved 2024-01-15
```

---

## Workflow 2: Digest

Goal: Summarize unread messages across all chats.

### Steps
1. Use `list_chats` to identify chats with unread messages.
2. Use `get_messages` or `list_messages` for each identified chat.
3. Generate a summary categorized by priority (Mentions, Updates, General).
4. (Optional) Draft replies using `save_draft`.

---

## Workflow 3: Style Extraction

Goal: Analyze channel posts to capture the user's writing style.

### Steps
1. Fetch the last 15-20 posts from a channel using `list_messages`.
2. Analyze language, structure, tone, length, and call-to-action patterns.
3. Save the findings to `references/style-guide.md`.

---

## Workflow 4: Post to Channel

Goal: Draft a post that matches the user's writing style.

### Steps
1. Read `references/style-guide.md`.
2. Generate a draft based on the user's topic.
3. Use `save_draft` to save the draft to the target channel for review.

---

## Workflow 5: Search and Reply

Goal: Locate specific messages and draft contextual replies.

### Steps
1. Use `search_messages` or `list_messages`.
2. Retrieve context using `get_message_context`.
3. Use `save_draft` with `reply_to_msg_id`.

---

## Safety and Security

1. **Draft-First Policy**: Use `save_draft` instead of `send_message` for important communications.
2. **Session Security**: The `anon.session` file provides account access. Keep it secure and do not commit it to version control.
3. **API Rate Limits**: Avoid excessive API calls to prevent temporary bans.
