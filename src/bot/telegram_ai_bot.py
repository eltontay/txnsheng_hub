from openai import OpenAI
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from github import Github
import os
from dotenv import load_dotenv
import base64

# Load environment variables
load_dotenv()

# Initialize clients
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
github = Github(os.getenv("GITHUB_TOKEN"))
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
REPO_NAME = os.getenv("REPO_NAME")

class TelegramAIBot:
    def __init__(self):
        self.repo = github.get_repo(REPO_NAME)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Hello! I'm your AI-powered repository assistant. I can help:\n"
            "1. Analyze new information and suggest README updates\n"
            "2. Create PRs with the changes\n\n"
            "To get started, use:\n"
            "/analyze <path/to/readme.md> <your information>"
        )

    async def analyze(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            # Split the command arguments
            args = context.args
            if len(args) < 2:
                await update.message.reply_text(
                    "Please provide both the README path and the information to analyze.\n"
                    "Example: /analyze docs/README.md Your information here"
                )
                return

            # Remove any leading slash from the path
            readme_path = args[0].lstrip('/')
            message = ' '.join(args[1:])

            # Get current README content
            try:
                file = self.repo.get_contents(readme_path, ref="main")
                current_content = file.decoded_content.decode()
            except Exception as e:
                await update.message.reply_text(f"Error: Could not find README at {readme_path}")
                return

            # Analyze with GPT
            analysis = await self.analyze_with_gpt(message, current_content, readme_path)
            
            # Store context for PR creation
            context.user_data['pending_analysis'] = {
                'content': analysis,
                'path': readme_path,  # Now using clean path without leading slash
                'file_sha': file.sha
            }
            
            await update.message.reply_text(
                "Here's my analysis:\n\n" + analysis + 
                "\n\nWould you like me to create a PR with these changes? (Reply with /createpr to confirm)"
            )

        except Exception as e:
            await update.message.reply_text(f"Error during analysis: {str(e)}")

    async def analyze_with_gpt(self, message: str, current_content: str, readme_path: str) -> str:
        prompt = f"""
        Analyze the following information and suggest how to integrate it into the README file.

        Current README content:
        {current_content}

        New information to integrate:
        {message}

        Please provide specific suggestions for updating the README while maintaining its current structure.
        Focus on where and how to add the new information.
        """

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.choices[0].message.content

    async def create_pr(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if 'pending_analysis' not in context.user_data:
            await update.message.reply_text("No pending changes to commit. Please use /analyze first!")
            return

        try:
            pending = context.user_data['pending_analysis']
            
            # Create new branch
            branch_name = f"update-{base64.b64encode(os.urandom(6)).decode('utf-8')}"
            source = self.repo.get_branch("main")
            
            # Create new branch from main
            self.repo.create_git_ref(f"refs/heads/{branch_name}", source.commit.sha)
            
            # Update file
            file = self.repo.get_contents(pending['path'], ref="main")
            self.repo.update_file(
                path=pending['path'],
                message="Update README via Telegram bot",
                content=pending['content'],
                sha=file.sha,
                branch=branch_name
            )
            
            # Create PR
            pr = self.repo.create_pull(
                title=f"Update {pending['path']}",
                body="AI-assisted update via Telegram bot",
                head=branch_name,
                base="main"
            )
            
            await update.message.reply_text(f"Created PR: {pr.html_url}")
            
            # Clear pending analysis
            del context.user_data['pending_analysis']
            
        except Exception as e:
            await update.message.reply_text(f"Error creating PR: {str(e)}")

    def run(self):
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("analyze", self.analyze))
        application.add_handler(CommandHandler("createpr", self.create_pr))
        
        # Run the bot
        application.run_polling() 