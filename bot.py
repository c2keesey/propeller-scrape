#!/usr/bin/env python3
"""
Telegram Bot Listener for Propeller Scrape

Listens for messages from an authorized Telegram chat and routes them
to a headless Claude Code session that can modify the propeller-scrape repo.
"""

import json
import os
import subprocess
import sys
import time
from functools import partial
from pathlib import Path

print = partial(print, flush=True)

from telegram_toolkit.telegram import TelegramNotifier

REPO_DIR = Path(__file__).parent
OFFSET_FILE = REPO_DIR / ".bot_offset"
SESSION_FILE = REPO_DIR / ".bot_session"
POLL_TIMEOUT = 30
CLAUDE_TIMEOUT = 300
MAX_MSG_LEN = 3900
BACKOFF_BASE = 2
BACKOFF_MAX = 60

CONTEXT_PREFIX = (
    "You are working in the propeller-scrape repository. "
    "This repo scrapes propeller.la/rewards for concert tickets in target cities "
    "(LA, SF, Boulder) and sends Telegram notifications for available shows. "
    "Key files: src/scraper.py (scraping logic), src/notifier.py (notifications), "
    "data/shows.json (tracked shows). "
    "Make the requested change. Keep your response concise (1-3 sentences)."
)


def find_claude_executable():
    """Find the claude CLI executable."""
    import shutil
    paths = [
        shutil.which("claude"),
        "/usr/local/bin/claude",
        f"{os.environ.get('HOME', '')}/.local/bin/claude",
    ]
    for path in paths:
        if path and os.path.exists(path):
            return path
    return None


def load_offset():
    if OFFSET_FILE.exists():
        try:
            return int(OFFSET_FILE.read_text().strip())
        except (ValueError, OSError):
            pass
    return None


def save_offset(offset):
    OFFSET_FILE.write_text(str(offset))


def load_session_id():
    if SESSION_FILE.exists():
        try:
            sid = SESSION_FILE.read_text().strip()
            print(f"Loaded session: {sid}")
            return sid
        except OSError:
            pass
    print("No existing session")
    return None


def save_session_id(session_id):
    SESSION_FILE.write_text(session_id)
    print(f"Saved session: {session_id}")


def clear_session():
    if SESSION_FILE.exists():
        SESSION_FILE.unlink()
    return None


def send_message(bot_token, chat_id, text):
    import requests

    api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    chunks = []
    while text:
        if len(text) <= MAX_MSG_LEN:
            chunks.append(text)
            break
        split_at = text.rfind("\n", 0, MAX_MSG_LEN)
        if split_at == -1:
            split_at = MAX_MSG_LEN
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip("\n")

    for chunk in chunks:
        requests.post(api_url, json={
            "chat_id": chat_id,
            "text": chunk,
            "disable_web_page_preview": True,
        }, timeout=10)


def get_updates(bot_token, offset):
    import requests

    params = {"timeout": POLL_TIMEOUT, "allowed_updates": ["message"]}
    if offset is not None:
        params["offset"] = offset
    resp = requests.get(
        f"https://api.telegram.org/bot{bot_token}/getUpdates",
        params=params,
        timeout=POLL_TIMEOUT + 10,
    )
    resp.raise_for_status()
    return resp.json().get("result", [])


def _build_claude_cmd(claude_path, message_text, session_id=None):
    cmd = [
        claude_path, "-p", message_text,
        "--dangerously-skip-permissions",
        "--output-format", "json",
        "--model", "claude-opus-4-6",
    ]

    if session_id:
        cmd.extend(["--resume", session_id])
    else:
        cmd.extend(["--system-prompt", CONTEXT_PREFIX])

    return cmd


def _run_claude_once(cmd):
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=CLAUDE_TIMEOUT,
        cwd=str(REPO_DIR),
        env={**os.environ, "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"},
    )
    if result.returncode != 0:
        return None, f"Claude failed (exit {result.returncode}):\n{result.stderr[-500:]}"

    try:
        data = json.loads(result.stdout)
        return data, None
    except json.JSONDecodeError:
        return None, result.stdout.strip()


def run_claude(message_text, session_id=None):
    claude_path = find_claude_executable()
    if not claude_path:
        return "Error: Claude CLI not found on this machine.", None

    cmd = _build_claude_cmd(claude_path, message_text, session_id)
    print(f"Claude cmd: resume={session_id is not None} session={session_id}")

    try:
        data, error = _run_claude_once(cmd)

        if error and session_id:
            print(f"Resume failed, starting fresh session: {error[:100]}")
            cmd = _build_claude_cmd(claude_path, message_text, session_id=None)
            data, error = _run_claude_once(cmd)

        if error:
            return error, session_id

        new_session_id = data.get("session_id", session_id)
        response_text = data.get("result", "")
        print(f"Claude response OK, session={new_session_id}")
        return response_text, new_session_id

    except subprocess.TimeoutExpired:
        return f"Claude timed out after {CLAUDE_TIMEOUT}s.", session_id
    except Exception as e:
        return f"Claude error: {e}", session_id


def git_changes():
    result = subprocess.run(
        ["git", "diff", "--stat"],
        capture_output=True, text=True, cwd=str(REPO_DIR),
    )
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, cwd=str(REPO_DIR),
    )
    return (result.stdout.strip() + "\n" + status.stdout.strip()).strip()


def git_commit_and_push(user_message):
    subprocess.run(["git", "add", "-A"], cwd=str(REPO_DIR), check=True)

    short_msg = user_message[:60].replace("\n", " ")
    commit_msg = f"Auto: {short_msg}"

    subprocess.run(
        ["git", "commit", "-m", commit_msg],
        cwd=str(REPO_DIR), check=True,
        capture_output=True, text=True,
    )

    push_result = subprocess.run(
        ["git", "push"],
        cwd=str(REPO_DIR),
        capture_output=True, text=True,
    )
    return push_result.returncode == 0, push_result.stderr.strip()


def handle_message(bot_token, chat_id, message_text):
    if message_text.strip().lower() == "/reset":
        clear_session()
        send_message(bot_token, chat_id, "Session cleared. Next message starts a fresh conversation.")
        return

    send_message(bot_token, chat_id, "Processing...")

    session_id = load_session_id()
    response, new_session_id = run_claude(message_text, session_id)

    if new_session_id and new_session_id != session_id:
        save_session_id(new_session_id)

    changes = git_changes()
    if changes:
        pushed, push_err = git_commit_and_push(message_text)
        diff_result = subprocess.run(
            ["git", "log", "-1", "--stat", "--format="],
            capture_output=True, text=True, cwd=str(REPO_DIR),
        )
        summary = diff_result.stdout.strip()

        commit_result = subprocess.run(
            ["git", "log", "-1", "--format=%s"],
            capture_output=True, text=True, cwd=str(REPO_DIR),
        )
        commit_subject = commit_result.stdout.strip()

        reply = response + "\n\n---\n"
        reply += f"Changed: {summary}\n"
        reply += f'Committed: "{commit_subject}"\n'
        if pushed:
            reply += "Pushed to origin"
        else:
            reply += f"Push failed: {push_err}"
    else:
        reply = response

    send_message(bot_token, chat_id, reply)


def main():
    print("Starting propeller-scrape bot...")

    notifier = TelegramNotifier(env_file=str(REPO_DIR / ".env"))
    bot_token = notifier.bot_token
    chat_id = notifier.chat_id

    print(f"Authorized chat_id: {chat_id}")

    offset = load_offset()
    retries = 0

    while True:
        try:
            updates = get_updates(bot_token, offset)
            retries = 0

            for update in updates:
                update_id = update["update_id"]
                offset = update_id + 1
                save_offset(offset)

                msg = update.get("message", {})
                msg_chat_id = str(msg.get("chat", {}).get("id", ""))
                text = msg.get("text", "")

                if msg_chat_id != str(chat_id):
                    continue

                if not text:
                    continue

                print(f"Received: {text[:80]}")
                try:
                    handle_message(bot_token, chat_id, text)
                except Exception as e:
                    print(f"Error handling message: {e}")
                    send_message(bot_token, chat_id, f"Error: {e}")

        except KeyboardInterrupt:
            print("\nShutting down.")
            sys.exit(0)
        except Exception as e:
            delay = min(BACKOFF_BASE ** (retries + 1), BACKOFF_MAX)
            print(f"Poll error: {e} — retrying in {delay}s")
            time.sleep(delay)
            retries += 1


if __name__ == "__main__":
    main()
