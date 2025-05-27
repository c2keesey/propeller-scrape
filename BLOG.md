# Building a Concert Scraper in 1 Hour (Writing Zero Code) with Claude Code

*Or: How I learned to stop worrying and love automation*

## The Challenge

I had a simple problem: I wanted to know when new concert tickets became available on Propeller's rewards site, but I'm too lazy to check manually. Classic engineer solution? Build something to do it for me.

The twist: I wanted to see if I could build this **without writing a single line of code myself**. Enter Claude Code, Anthropic's CLI tool that can read, write, and execute code in your terminal.

## What We Built (In ~1 Hour)

A complete web scraper that:
- 🕷️ Scrapes Propeller's rewards page for new concert listings
- 📍 Filters for shows in LA, SF, and Boulder (my target cities)
- 🔍 Analyzes individual show pages for venue details and ticket availability
- 📱 Sends Telegram notifications when new shows appear
- ⏰ Runs automatically via cron job
- 📊 Tracks seen shows in local JSON storage
- 🚨 Includes error handling and logging

## The Experience: Zero Code, Maximum Learning

Here's the wild part: I literally wrote **zero code**. I described what I wanted, and Claude Code:
- Set up the entire Python project structure
- Wrote the web scraping logic with BeautifulSoup
- Implemented multi-platform notifications (Telegram, macOS, terminal)
- Created a robust cron wrapper script with logging
- Even handled edge cases like duplicate show detection

### What I Learned (Without Googling!)

**Telegram Bot API**: Never used it before. Claude walked me through:
- Creating a bot via @BotFather
- Getting bot tokens and chat IDs  
- Sending formatted messages with emojis and markdown

**Cron Job Gotchas**: Turns out cron is trickier than expected:
- Cron has a minimal PATH (no `uv` command found!)
- Requires absolute paths everywhere
- Environment variables need to be explicitly loaded
- Working directory isn't what you expect

**Modern Python Tooling**: Got introduced to `uv` as a faster pip/poetry alternative that Claude preferred over traditional tools.

## Where Claude Struggled (Brief Debugging Moments)

**The Cron PATH Mystery**: Claude initially assumed cron would find `uv` in PATH like my shell does. After several "command not found" errors, we discovered cron's minimal environment needs full paths (`/opt/homebrew/bin/uv`).

**JSON Syntax Slips**: Occasionally left trailing commas when editing JSON, causing parser errors. Quick fixes though!

## The Magic Moments

### Real-Time Debugging
When the scraper failed, I could just say "getting error still" and Claude would:
- Check the log files
- Identify the issue
- Fix it immediately
- Test the solution

### Iterative Improvement
"Make the notifications more detailed" → Instant emoji-rich Telegram messages with venue info and availability status.

"Add automation" → Complete cron setup with error handling and log rotation.

### Learning Through Building
Instead of reading tutorials about Telegram bots or cron jobs, I learned by building something I actually wanted. Claude explained concepts as we hit them in practice.

## The Result

After 1 hour, I had a production-ready scraper that:
- Actually works (getting notifications as I write this!)
- Has proper error handling and logging
- Includes comprehensive documentation
- Could be deployed to cloud services for 24/7 operation

**Total cost**: $1.21 (mostly from Claude's web scraping and code generation)

## Why This Was Cool

### The Interface
Claude Code's CLI interface is *chef's kiss*. What I particularly love:

- **Terminal-style edits**: Clean diffs showing exactly what changed, feels natural in CLI workflow
- **Real-time token feedback**: I can see costs/usage as we go, no surprises
- **Clear tool calls**: Every file read, bash command, edit is explicitly shown—total transparency
- **Seamless command switching**: From Python debugging to bash commands to git operations without breaking flow

Claude has always been excellent at using shell commands as project tools, and Claude Code makes that superpower accessible in a dedicated interface. It even helped set up the full git repo structure!

### My New Workflow Philosophy
I still use Cursor for production code where I need fine-grained control and collaboration features. But for small personal projects like this? Claude Code is becoming my go-to. It's perfect for:
- Quick automation scripts
- Learning new technologies by building
- Prototyping ideas rapidly
- "I wonder if I can build X" moments

### The Learning Experience
This felt like pair programming with someone who:
- Never gets tired of debugging PATH issues
- Knows every Python library by heart
- Can switch between coding, system administration, and documentation seamlessly
- Actually enjoys fixing JSON syntax errors

The goal wasn't to avoid learning—it was to learn by building instead of by reading. I now understand cron jobs, Telegram bots, and modern Python tooling because I used them to solve a real problem.

## Try It Yourself

The code is all here if you want to scrape your own concert alerts. Or better yet, try building something with Claude Code and see what you can create without writing code yourself.

*Now if you'll excuse me, I need to go check if any good shows just dropped in SF...*

---

*P.S. - This blog post was also written by Claude Code. Meta? Maybe. Efficient? Absolutely.*

**Tech Stack**: Python, BeautifulSoup, requests, Telegram Bot API, cron, uv package manager  
**Time**: ~1 hour  
**Lines of code written by human**: 0  
**New things learned**: 4-5  
**Concert tickets found**: TBD 🎵