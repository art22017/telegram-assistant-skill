#!/usr/bin/env python3
"""
Telegram Client for Advanced Search & Scraping

This script provides:
- One-time authentication (session stored in anon.session)
- Global search across all dialogs
- Scraping "Saved Messages" by date
- Structured JSON output for easy parsing

Usage:
    python telegram_client.py --auth                          # Initial login
    python telegram_client.py --search "keywords"            # Search all chats
    python telegram_client.py --search "keywords" --chat-id 123456  # Search specific chat
    python telegram_client.py --scrape-saved 2024-01-15     # Scrape by date
"""

import asyncio
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import argparse

from telethon import TelegramClient
from telethon.tl.types import PeerUser, PeerChat, PeerChannel


class TelegramSearchClient:
    def __init__(self, api_id: int, api_hash: str, session_name: str = "anon"):
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_name = session_name
        self.client = None

    async def connect(self):
        """Connect to Telegram. If session doesn't exist, prompt for login."""
        self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)
        
        # Check if session file exists
        session_file = Path(f"{self.session_name}.session")
        
        if not session_file.exists():
            print("[INFO] No existing session found. Starting authentication...")
            await self.client.start()
            print("[INFO] Session saved. You can now use this client without re-authenticating.")
        else:
            print("[INFO] Using existing session...")
            await self.client.start()

    async def disconnect(self):
        """Disconnect from Telegram."""
        if self.client:
            await self.client.disconnect()

    async def search_global(self, query: str, chat_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search for messages containing query text.
        
        Args:
            query: Search keyword(s)
            chat_id: Optional specific chat ID. If None, search all dialogs.
        
        Returns:
            List of matching messages with context.
        """
        results = []
        
        if chat_id:
            # Search in specific chat
            dialogs = [dialog for dialog in await self.client.get_dialogs() if dialog.id == chat_id]
            if not dialogs:
                return {"error": f"Chat ID {chat_id} not found", "results": []}
        else:
            # Search all dialogs
            dialogs = await self.client.get_dialogs()
        
        for dialog in dialogs:
            chat_title = dialog.title or f"Chat {dialog.id}"
            chat_id_val = dialog.id
            
            try:
                # Search messages in this dialog
                async for message in self.client.iter_messages(dialog.entity, search=query, limit=100):
                    if message and message.text:
                        results.append({
                            "chat_id": chat_id_val,
                            "chat_title": chat_title,
                            "message_id": message.id,
                            "text": message.text[:500],  # First 500 chars
                            "date": message.date.isoformat() if message.date else None,
                            "sender_id": message.sender_id,
                        })
            except Exception as e:
                # Skip chats we can't access
                pass
        
        return {"query": query, "results": results, "total": len(results)}

    async def scrape_saved_messages(self, target_date: str) -> Dict[str, Any]:
        """
        Scrape "Saved Messages" for a specific date.
        Retrieves all messages from that date, even if read.
        
        Args:
            target_date: Date in format YYYY-MM-DD
        
        Returns:
            Dict with messages from that date
        """
        try:
            # Parse target date
            date_obj = datetime.strptime(target_date, "%Y-%m-%d")
            start_of_day = date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = date_obj.replace(hour=23, minute=59, second=59, microsecond=999999)
        except ValueError:
            return {
                "error": "Invalid date format. Use YYYY-MM-DD",
                "results": []
            }
        
        # Get current user (Saved Messages is typically the user's own chat)
        me = await self.client.get_me()
        saved_messages_id = me.id
        
        results = []
        
        try:
            # Fetch messages from Saved Messages
            async for message in self.client.iter_messages(saved_messages_id, limit=None):
                if message and message.date:
                    msg_date = message.date.replace(tzinfo=None)
                    
                    # Check if message is within target date
                    if start_of_day <= msg_date <= end_of_day:
                        results.append({
                            "message_id": message.id,
                            "text": message.text or "",
                            "date": message.date.isoformat(),
                            "is_read": not message.out,  # Rough heuristic
                            "media_type": message.media.__class__.__name__ if message.media else None,
                        })
                    
                    # Stop if we've passed the target date (older messages)
                    if msg_date < start_of_day:
                        break
        except Exception as e:
            return {
                "error": f"Failed to scrape Saved Messages: {str(e)}",
                "results": []
            }
        
        return {
            "date": target_date,
            "results": results,
            "total": len(results)
        }

    async def get_me(self) -> Dict[str, Any]:
        """Get current user info."""
        me = await self.client.get_me()
        return {
            "user_id": me.id,
            "first_name": me.first_name,
            "last_name": me.last_name,
            "username": me.username,
            "phone": me.phone,
        }


async def main():
    parser = argparse.ArgumentParser(
        description="Telegram Search & Scrape Client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python telegram_client.py --auth
  python telegram_client.py --search "keyword"
  python telegram_client.py --search "keyword" --chat-id 123456
  python telegram_client.py --scrape-saved 2024-01-15
  python telegram_client.py --whoami
        """
    )
    
    parser.add_argument("--auth", action="store_true", help="Authenticate and save session")
    parser.add_argument("--search", type=str, help="Search all chats for keyword(s)")
    parser.add_argument("--chat-id", type=int, help="Limit search to specific chat ID")
    parser.add_argument("--scrape-saved", type=str, help="Scrape Saved Messages by date (YYYY-MM-DD)")
    parser.add_argument("--whoami", action="store_true", help="Display current user info")
    parser.add_argument("--api-id", type=int, help="Telegram API ID (or set TELEGRAM_API_ID env var)")
    parser.add_argument("--api-hash", type=str, help="Telegram API Hash (or set TELEGRAM_API_HASH env var)")
    
    args = parser.parse_args()
    
    # Get API credentials from args or environment
    import os
    api_id = args.api_id or os.getenv("TELEGRAM_API_ID")
    api_hash = args.api_hash or os.getenv("TELEGRAM_API_HASH")
    
    if not api_id or not api_hash:
        print("ERROR: TELEGRAM_API_ID and TELEGRAM_API_HASH must be set")
        print("Set them as environment variables or pass --api-id and --api-hash")
        sys.exit(1)
    
    try:
        api_id = int(api_id)
    except (ValueError, TypeError):
        print("ERROR: TELEGRAM_API_ID must be an integer")
        sys.exit(1)
    
    client = TelegramSearchClient(api_id, api_hash)
    
    try:
        await client.connect()
        
        if args.auth:
            # Just authenticate
            me = await client.get_me()
            print(json.dumps({
                "status": "authenticated",
                "user": me,
                "session_file": f"{client.session_name}.session"
            }, indent=2, ensure_ascii=False))
        
        elif args.whoami:
            me = await client.get_me()
            print(json.dumps(me, indent=2, ensure_ascii=False))
        
        elif args.search:
            results = await client.search_global(args.search, args.chat_id)
            print(json.dumps(results, indent=2, ensure_ascii=False))
        
        elif args.scrape_saved:
            results = await client.scrape_saved_messages(args.scrape_saved)
            print(json.dumps(results, indent=2, ensure_ascii=False))
        
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(json.dumps({
            "error": str(e),
            "error_type": type(e).__name__
        }, indent=2))
        sys.exit(1)
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

