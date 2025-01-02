from openai import OpenAI
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from github import Github
import os
from dotenv import load_dotenv
import base64
import logging
from datetime import datetime
import json
from pathlib import Path

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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
        self.allowed_users = self.load_allowed_users()
        logger.info(f"Bot initialized for repository: {REPO_NAME}")
        logger.info(f"Loaded {len(self.allowed_users['allowed_handles'])} allowed users")

    def load_allowed_users(self) -> dict:
        """Load allowed users from config file"""
        try:
            config_path = Path(__file__).parent / "config" / "allowed_users.json"
            with open(config_path, 'r') as f:
                users = json.load(f)
            return users
        except Exception as e:
            logger.error(f"Error loading allowed users: {str(e)}")
            return {"allowed_handles": [], "admin_handles": []}

    def save_allowed_users(self):
        """Save current allowed users to config file"""
        try:
            config_path = Path(__file__).parent / "config" / "allowed_users.json"
            with open(config_path, 'w') as f:
                json.dump(self.allowed_users, f, indent=4)
            logger.info("Saved updated allowed users list")
        except Exception as e:
            logger.error(f"Error saving allowed users: {str(e)}")

    async def check_access(self, user) -> bool:
        """Check if user has access based on handle"""
        if user.username in self.allowed_users['allowed_handles']:
            logger.info(f"Access granted to @{user.username}")
            return True
        logger.warning(f"Access denied for @{user.username}")
        return False

    async def check_admin(self, user) -> bool:
        """Check if user is admin"""
        return user.username in self.allowed_users['admin_handles']

    async def add_allowed_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add new allowed user (admin only)"""
        user = update.effective_user
        if not await self.check_admin(user):
            await update.message.reply_text("Only admins can add new users.")
            return

        if not context.args:
            await update.message.reply_text("Please provide a username: /adduser username")
            return

        new_user = context.args[0].replace('@', '')
        if new_user not in self.allowed_users['allowed_handles']:
            self.allowed_users['allowed_handles'].append(new_user)
            self.save_allowed_users()
            await update.message.reply_text(f"Added @{new_user} to allowed users.")
            logger.info(f"Admin @{user.username} added new user @{new_user}")
        else:
            await update.message.reply_text(f"@{new_user} is already an allowed user.")

    async def remove_allowed_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Remove allowed user (admin only)"""
        user = update.effective_user
        if not await self.check_admin(user):
            await update.message.reply_text("Only admins can remove users.")
            return

        if not context.args:
            await update.message.reply_text("Please provide a username: /removeuser username")
            return

        remove_user = context.args[0].replace('@', '')
        if remove_user in self.allowed_users['allowed_handles']:
            self.allowed_users['allowed_handles'].remove(remove_user)
            self.save_allowed_users()
            await update.message.reply_text(f"Removed @{remove_user} from allowed users.")
            logger.info(f"Admin @{user.username} removed user @{remove_user}")
        else:
            await update.message.reply_text(f"@{remove_user} is not in allowed users.")

    async def list_allowed_users(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List all allowed users (admin only)"""
        user = update.effective_user
        if not await self.check_admin(user):
            await update.message.reply_text("Only admins can view user list.")
            return

        users_list = "\n".join([f"@{u}" for u in self.allowed_users['allowed_handles']])
        await update.message.reply_text(
            f"Allowed Users:\n{users_list}\n\n"
            f"Total: {len(self.allowed_users['allowed_handles'])} users"
        )

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        is_admin = await self.check_admin(user)
        
        # Check handle-based access
        if not await self.check_access(user):
            await update.message.reply_text(
                "Access denied. This bot is only available to specific users.\n"
                "Please contact @txnsheng for access."
            )
            return

        logger.info(f"New user started bot: {user.id} - {user.username}")
        
        # Different messages for admin and regular users
        if is_admin:
            await update.message.reply_text(
                "Hello Admin! I'm your AI-powered repository assistant. Here are your available commands:\n\n"
                "Repository Management:\n"
                "/repoStructure - Show repository structure with MD files\n\n"
                
                "Content Management:\n"
                "/analyzeContent - Analyze and suggest updates\n"
                "Format:\n"
                "/analyzeContent path/to/file.md\n"
                "Your content here...\n"
                "Can span multiple lines\n"
                "With proper formatting\n\n"
                
                "PR Management:\n"
                "/createPr - Create a PR with pending changes\n"
                "/listPrs - Show all open PRs\n"
                "/mergePr <number> - Merge a specific PR\n"
                "/closePr <number> - Close a specific PR\n\n"
                
                "Admin Commands:\n"
                "/addUser <username> - Add new allowed user\n"
                "/removeUser <username> - Remove allowed user\n"
                "/listUsers - Show all allowed users\n\n"
                
                "Example usage:\n"
                "/analyzeContent data/research/README.md\n"
                "Here's my research about XYZ...\n"
                "It can span multiple lines\n\n"
                "And have proper formatting\n\n"
                "- Even bullet points\n"
                "- And lists"
            )
        else:
            await update.message.reply_text(
                "Hello! I'm your AI-powered repository assistant.\n\n"
                "Please contact @txnsheng for admin access to use the bot's features."
            )

    async def analyze(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            user = update.effective_user
            if not await self.check_admin(user):
                await update.message.reply_text("Only admins can analyze content.")
                return
            logger.info(f"Analysis requested by user {user.username}")
            
            # Get full message text
            full_text = update.message.text
            
            # Remove the command from the start
            command_end = full_text.find(' ')
            if command_end == -1:
                await update.message.reply_text(
                    "Please provide both the README path and the information to analyze.\n"
                    "Format: /analyzeContent path/to/file.md\n"
                    "Your content here...\n"
                    "Can span multiple lines..."
                )
                return
            
            # Split into path and content
            text_parts = full_text[command_end + 1:].strip().split('\n', 1)
            if len(text_parts) < 2:
                await update.message.reply_text(
                    "Please provide the content in a new line after the path.\n"
                    "Example:\n"
                    "/analyzeContent docs/README.md\n"
                    "Your content here...\n"
                    "Can span multiple lines..."
                )
                return
            
            readme_path = text_parts[0].strip()
            message = text_parts[1].strip()

            # Remove any leading slash from the path
            readme_path = readme_path.lstrip('/')

            # Get current README content
            try:
                file = self.repo.get_contents(readme_path, ref="main")
                current_content = file.decoded_content.decode()
            except Exception as e:
                await update.message.reply_text(f"Error: Could not find README at {readme_path}")
                return

            # Analyze with GPT
            analysis = await self.analyze_with_gpt(message, current_content, readme_path)
            
            # Create keyboard for actions
            keyboard = [
                [
                    InlineKeyboardButton("Create PR", callback_data=f"create_pr_{readme_path}"),
                    InlineKeyboardButton("Improve Suggestion", callback_data=f"improve_{readme_path}"),
                    InlineKeyboardButton("Cancel", callback_data="cancel")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Store context for PR creation
            context.user_data['pending_analysis'] = {
                'content': analysis,
                'path': readme_path,
                'file_sha': file.sha,
                'original_message': message
            }
            
            await update.message.reply_text(
                "Here's my suggested content:\n\n" + analysis + 
                "\n\nWhat would you like to do?",
                reply_markup=reply_markup
            )

            logger.info(f"Analysis completed for {readme_path}")

        except Exception as e:
            logger.error(f"Error during analysis: {str(e)}", exc_info=True)
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
        try:
            user = update.effective_user
            if not await self.check_admin(user):
                await update.message.reply_text("Only admins can create PRs.")
                return
            logger.info(f"PR creation requested by user {user.username}")
            
            if 'pending_analysis' not in context.user_data:
                await update.message.reply_text("No pending changes to commit. Please use /analyze first!")
                return

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
            
            logger.info(f"Successfully created PR: {pr.html_url}")

        except Exception as e:
            logger.error(f"Error creating PR: {str(e)}", exc_info=True)
            await update.message.reply_text(f"Error creating PR: {str(e)}")

    async def list_prs(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            user = update.effective_user
            if not await self.check_admin(user):
                await update.message.reply_text("Only admins can list PRs.")
                return
            logger.info(f"PR list requested by user {user.username}")
            
            pulls = self.repo.get_pulls(state='open')
            logger.info(f"Found {pulls.totalCount} open PRs")
            
            if pulls.totalCount == 0:
                await update.message.reply_text("No open pull requests found.")
                return

            message = "Open Pull Requests:\n\n"
            for pr in pulls:
                # Create inline keyboard buttons for each PR
                keyboard = [
                    [
                        InlineKeyboardButton("Merge", callback_data=f"merge_{pr.number}"),
                        InlineKeyboardButton("Close", callback_data=f"close_{pr.number}")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                message = (f"#{pr.number}: {pr.title}\n"
                         f"Status: {pr.state}\n"
                         f"URL: {pr.html_url}\n")
                
                await update.message.reply_text(message, reply_markup=reply_markup)

        except Exception as e:
            logger.error(f"Error listing PRs: {str(e)}", exc_info=True)
            await update.message.reply_text(f"Error listing PRs: {str(e)}")

    async def merge_pr(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            user = update.effective_user
            if not await self.check_admin(user):
                await update.message.reply_text("Only admins can merge PRs.")
                return
            pr_number = int(context.args[0])
            logger.info(f"PR #{pr_number} merge requested by user {user.username}")
            
            pr = self.repo.get_pull(pr_number)

            if not pr.mergeable:
                await update.message.reply_text("This PR cannot be merged. Please check for conflicts.")
                return

            pr.merge(merge_method='squash')
            await update.message.reply_text(f"Successfully merged PR #{pr_number}")

            logger.info(f"Successfully merged PR #{pr_number}")

        except Exception as e:
            logger.error(f"Error merging PR: {str(e)}", exc_info=True)
            await update.message.reply_text(f"Error merging PR: {str(e)}")

    async def close_pr(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            user = update.effective_user
            if not await self.check_admin(user):
                await update.message.reply_text("Only admins can close PRs.")
                return
            pr_number = int(context.args[0])
            logger.info(f"PR #{pr_number} close requested by user {user.username}")
            
            pr = self.repo.get_pull(pr_number)
            pr.edit(state='closed')
            await update.message.reply_text(f"Successfully closed PR #{pr_number}")

            logger.info(f"Successfully closed PR #{pr_number}")

        except Exception as e:
            logger.error(f"Error closing PR: {str(e)}", exc_info=True)
            await update.message.reply_text(f"Error closing PR: {str(e)}")

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            query = update.callback_query
            user = query.from_user
            
            if not await self.check_admin(user):
                await query.answer("Only admins can perform this action.")
                return
                
            logger.info(f"Button callback from user {user.username}: {query.data}")
            
            await query.answer()

            if query.data.startswith("create_pr_"):
                # Create PR with the current suggestion
                if 'pending_analysis' in context.user_data:
                    pending = context.user_data['pending_analysis']
                    branch_name = f"update-{base64.b64encode(os.urandom(6)).decode('utf-8')}"
                    source = self.repo.get_branch("main")
                    
                    self.repo.create_git_ref(f"refs/heads/{branch_name}", source.commit.sha)
                    
                    file = self.repo.get_contents(pending['path'], ref="main")
                    self.repo.update_file(
                        path=pending['path'],
                        message="Update content via Telegram bot",
                        content=pending['content'],  # This now contains only the suggested content
                        sha=file.sha,
                        branch=branch_name
                    )
                    
                    pr = self.repo.create_pull(
                        title=f"Update {pending['path']}",
                        body="AI-assisted update via Telegram bot",
                        head=branch_name,
                        base="main"
                    )
                    
                    await query.edit_message_text(f"Created PR: {pr.html_url}")
                    del context.user_data['pending_analysis']
                
            elif query.data.startswith("improve_"):
                # Get improved suggestion
                if 'pending_analysis' in context.user_data:
                    pending = context.user_data['pending_analysis']
                    improved_analysis = await self.analyze_with_gpt(
                        f"Please improve this suggestion:\n{pending['content']}",
                        pending['original_message'],
                        pending['path']
                    )
                    
                    # Update stored content
                    context.user_data['pending_analysis']['content'] = improved_analysis
                    
                    # Show new suggestion with same buttons
                    keyboard = [
                        [
                            InlineKeyboardButton("Create PR", callback_data=f"create_pr_{pending['path']}"),
                            InlineKeyboardButton("Improve Suggestion", callback_data=f"improve_{pending['path']}"),
                            InlineKeyboardButton("Cancel", callback_data="cancel")
                        ]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await query.edit_message_text(
                        f"Here's my improved suggestion:\n\n{improved_analysis}\n\nWhat would you like to do?",
                        reply_markup=reply_markup
                    )
            
            elif query.data == "cancel":
                if 'pending_analysis' in context.user_data:
                    del context.user_data['pending_analysis']
                await query.edit_message_text("Analysis cancelled.")

        except Exception as e:
            logger.error(f"Error in button callback: {str(e)}", exc_info=True)
            await query.edit_message_text(f"Error processing request: {str(e)}")

    async def get_repo_structure(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show repository structure up to MD files"""
        try:
            user = update.effective_user
            if not await self.check_admin(user):
                await update.message.reply_text("Only admins can view repository structure.")
                return

            logger.info(f"Repository structure requested by admin {user.username}")

            def get_data_structure(path=""):
                contents = self.repo.get_contents(path)
                tree = ""
                for content in contents:
                    # Only process data directory and its contents
                    if content.name == "data":
                        tree += f"📁 {content.name}/\n"
                        try:
                            subcontents = self.repo.get_contents(content.path)
                            for subcontent in subcontents:
                                if subcontent.type == "dir":
                                    tree += f"    📁 {subcontent.name}/\n"
                                    try:
                                        subsubcontents = self.repo.get_contents(subcontent.path)
                                        for subsubcontent in subsubcontents:
                                            if subsubcontent.name.endswith('.md'):
                                                tree += f"        📄 {subsubcontent.name}\n"
                                    except Exception as e:
                                        logger.warning(f"Error accessing {subcontent.path}: {str(e)}")
                        except Exception as e:
                            logger.warning(f"Error accessing {content.path}: {str(e)}")
                return tree

            structure = "Repository Structure:\n\n"
            structure += get_data_structure()

            await update.message.reply_text(structure)
            logger.info("Repository structure sent successfully")

        except Exception as e:
            logger.error(f"Error getting repository structure: {str(e)}", exc_info=True)
            await update.message.reply_text(f"Error getting repository structure: {str(e)}")

    def run(self):
        logger.info("Starting bot...")
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Add handlers with new command names
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("analyzeContent", self.analyze))
        application.add_handler(CommandHandler("createPr", self.create_pr))
        application.add_handler(CommandHandler("listPrs", self.list_prs))
        application.add_handler(CommandHandler("mergePr", self.merge_pr))
        application.add_handler(CommandHandler("closePr", self.close_pr))
        
        # User management handlers
        application.add_handler(CommandHandler("addUser", self.add_allowed_user))
        application.add_handler(CommandHandler("removeUser", self.remove_allowed_user))
        application.add_handler(CommandHandler("listUsers", self.list_allowed_users))
        
        # Add new handler
        application.add_handler(CommandHandler("repoStructure", self.get_repo_structure))
        
        application.add_handler(CallbackQueryHandler(self.button_callback))
        
        logger.info("Bot is ready! Starting polling...")
        application.run_polling() 