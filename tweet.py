#!/usr/bin/env python3
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import tweepy

script_dir = Path(__file__).parent
env_path = script_dir / '.env.local'
load_dotenv(dotenv_path=env_path, override=True)

# --- CONFIGURATION ---
API_KEY = os.getenv('TWITTER_API_KEY')
API_SECRET = os.getenv('TWITTER_API_KEY_SECRET')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ACCESS_SECRET = os.getenv('ACCESS_TOKEN_SECRET')

TWEET_LIMIT = 280  # basic counter (X is more complex, but this is good enough)


def create_client() -> tweepy.Client:
    return tweepy.Client(
        consumer_key=API_KEY,
        consumer_secret=API_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_SECRET
    )


def send_tweet(tweet_text: str) -> None:
    client = create_client()
    response = client.create_tweet(text=tweet_text)
    print(f"✅ Tweet sent! ID: {response.data['id']}")


def interactive_compose() -> str | None:
    """
    Simple REPL-like tweet composer.

    Controls:
      - Type your tweet, multiple lines allowed
      - `/send` on an empty line → finish and send
      - `/clear` → clear current text
      - `/quit` or Ctrl+D → abort without sending
    """
    print("=== Tweet composer ===")
    print("Type your tweet. Multi-line is allowed.")
    print("Commands: /send, /clear, /quit")
    print("(Ctrl+D also quits)\n")

    lines: list[str] = []

    while True:
        try:
            # Visual prompt like Python REPL: >>> for first line, ... for others
            prompt = ">>> " if not lines else "... "
            line = input(prompt)
        except EOFError:
            print("\nAborted.")
            return None

        # Handle commands
        if line.strip() == "/quit":
            print("Aborted.")
            return None
        if line.strip() == "/clear":
            lines.clear()
            print("[cleared]")
            continue
        if line.strip() == "/send":
            tweet_text = "\n".join(lines).strip()
            if not tweet_text:
                print("⚠️  Nothing to send.")
                continue
            return tweet_text

        # Normal text line
        lines.append(line)
        tweet_text = "\n".join(lines)
        length = len(tweet_text)
        over = length - TWEET_LIMIT

        if over > 0:
            print(f"[{length} chars, {over} over {TWEET_LIMIT} ⚠️]")
        else:
            remaining = TWEET_LIMIT - length
            print(f"[{length} chars, {remaining} left]")


def main():
    # --- Mode 1: no args → interactive compose mode ---
    if len(sys.argv) == 1:
        tweet_text = interactive_compose()
        if tweet_text is None:
            return
        try:
            send_tweet(tweet_text)
        except Exception as e:
            print(f"❌ Error: {e}")
        return

    # --- Mode 2: with args → one-liner via CLI ---
    tweet_text = " ".join(sys.argv[1:])
    if not tweet_text.strip():
        print("Error: No text provided.")
        print("Usage: python tweet.py \"Hello World\"")
        return

    try:
        send_tweet(tweet_text)
    except Exception as e:
        print(f"❌ Erroxr: {e}")


if __name__ == "__main__":
    main()
