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

This repository includes a Telegram bot that helps manage and update content through AI-assisted analysis. Access is limited to approved users only.

### Bot Commands

#### Content Management
- `/analyzeContent` - Analyze and suggest updates
  ```
  Format:
  /analyzeContent path/to/file.md
  Your content here...
  Can span multiple lines
  With proper formatting
  ```

#### PR Management
- `/createPr` - Create a pull request with changes
- `/listPrs` - Show all open pull requests
- `/mergePr <number>` - Merge a specific PR
- `/closePr <number>` - Close a specific PR

#### Admin Commands
- `/addUser <username>` - Add new allowed user
- `/removeUser <username>` - Remove allowed user
- `/listUsers` - Show all allowed users

### Example Usage
```
/analyzeContent data/research/README.md
Here's my research about XYZ...
It can span multiple lines

And have proper formatting

- Even bullet points
- And lists
```

## Development Setup

### Prerequisites
- Python 3.8+
- OpenAI API key
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- GitHub Personal Access Token
- Access permission from [@txnsheng](https://t.me/txnsheng)

### Local Development
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
python backend/src/bot/main.py
```

## Project Structure
```
txnsheng_hub/
├── backend/
│   └── src/
│       └── bot/
│           ├── config/
│           │   └── allowed_users.json
│           ├── main.py
│           └── telegram_ai_bot.py
├── data/
│   ├── work/
│   ├── research/
│   └── ecosystem/
├── .env.example
├── .gitignore
├── README.md
├── railway.toml
└── requirements.txt
```

## Contributing

I welcome collaborations and contributions! If you'd like to work together or suggest improvements:

1. Check the [progress tracker](data/prompt/progress.md) for current status
2. [Open a new issue](https://github.com/eltontay/txnsheng_hub/issues) with your proposal
3. Submit a pull request

Looking forward to collaborating with you! 🚀