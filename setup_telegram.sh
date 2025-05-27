#!/bin/bash

echo "🤖 Telegram Bot Setup for Propeller Scraper"
echo "==========================================="
echo ""

echo "Step 1: Create your bot"
echo "1. Open Telegram and search for @BotFather"
echo "2. Send /newbot and follow the prompts"
echo "3. Save your bot token (looks like: 123456789:ABCdefGHI...)"
echo ""

read -p "Enter your bot token: " BOT_TOKEN

echo ""
echo "Step 2: Get your chat ID"
echo "1. Send any message to your bot in Telegram"
echo "2. Visit this URL in your browser:"
echo "   https://api.telegram.org/bot${BOT_TOKEN}/getUpdates"
echo "3. Look for \"chat\":{\"id\":12345678 - that number is your chat ID"
echo ""

read -p "Enter your chat ID: " CHAT_ID

echo ""
echo "Setting up environment variables..."

# Add to .env file
cat > .env << EOF
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=${BOT_TOKEN}
TELEGRAM_CHAT_ID=${CHAT_ID}
EOF

# Add to shell profile for persistent use
echo "" >> ~/.zshrc
echo "# Propeller Scraper Telegram Config" >> ~/.zshrc
echo "export TELEGRAM_BOT_TOKEN='${BOT_TOKEN}'" >> ~/.zshrc
echo "export TELEGRAM_CHAT_ID='${CHAT_ID}'" >> ~/.zshrc

echo ""
echo "✅ Setup complete!"
echo ""
echo "Environment variables added to:"
echo "- .env (for local development)"
echo "- ~/.zshrc (for terminal sessions)"
echo ""
echo "To test notifications, run:"
echo "  source .env && uv run python src/notifier.py"
echo ""
echo "Or restart your terminal and run:"
echo "  uv run python src/notifier.py"