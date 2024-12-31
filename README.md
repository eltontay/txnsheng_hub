# Txnsheng Hub

Welcome to the Txnsheng ('transact-sheng') Hub repository! This repository serves as a comprehensive information hub for [@txnsheng](https://twitter.com/txnsheng), encompassing work, knowledge, research, interests, and more.

**Disclaimer**: All thoughts, opinions, and interests expressed in this repository are personal and do not represent the views of any company or organization that I am affiliated with.

## Contents

### [Work](data/work/)
  - [Circle](data/work/circle/) - *Developer Relations Lead, APAC* - Present
  - [Polygon](data/work/polygon/) - *Developer Relations Engineer*

### [Research](data/research/)
  - [Hyperliquid](data/research/hyperliquid/README.md)

### [Ecosystem](data/ecosystem/)
- **Alpha Communities**
  - [Cookies Reads](https://t.me/cookiesreads) - Research-focused crypto insights by [@jinglingcookies](https://x.com/jinglingcookies)
  - [Kirby Crypto](https://t.me/kirbycrypto) - Latest news and alpha by [@kirbyongeo](https://x.com/kirbyongeo)

## Telegram Bot Integration

This repository includes a Telegram bot that helps manage and update content through AI-assisted analysis. Here's how to set it up:

### Prerequisites
- Python 3.8+
- OpenAI API key
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- GitHub Personal Access Token

### Installation

1. Clone the repository:
```bash
git clone https://github.com/eltontay/txnsheng_hub.git
cd txnsheng_hub
```


2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install requirements:
```bash
pip install -r requirements.txt
```

4. Create `.env` file in the root directory:
```env
OPENAI_API_KEY=your_openai_api_key
TELEGRAM_TOKEN=your_telegram_bot_token
GITHUB_TOKEN=your_github_personal_access_token
REPO_NAME=username/repo-name
```

5. Run the bot:
```bash
python src/bot/main.py
```

### Using the Bot

1. Start a chat with your bot on Telegram

2. Use `/start` to see available commands

3. Use `/analyze path/to/readme.md Your information` to analyze and suggest updates

4. Use `/createpr` to create a pull request with the changes

## Contributing

I welcome collaborations and contributions! If you'd like to work together or suggest improvements, please [open a new issue](https://github.com/eltontay/txnsheng_hub/issues) with your proposal.

Looking forward to collaborating with you! 🚀