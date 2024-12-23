import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from datetime import datetime, timedelta

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory storage for reminders and tasks
reminders = {}

# Start command handler
async def start(update: Update, context: CallbackContext) -> None:
    """Send a welcome message when /start command is issued."""
    await update.message.reply_text('Hello! I am your assistant bot. Use /help for instructions.')

# Help command handler
async def help(update: Update, context: CallbackContext) -> None:
    """Send a help message when /help command is issued."""
    help_text = (
        "I can assist you with the following commands:\n"
        "/start - Start interacting with the bot.\n"
        "/help - List all available commands.\n"
        "/remindme <time> <message> - Set a reminder (e.g., /remindme 10m Take a break).\n"
        "/tasks - View your tasks.\n"
        "/addtask <task> - Add a new task.\n"
        "/status - View current status of tasks and reminders.\n"
    )
    await update.message.reply_text(help_text)

# Reminder functionality
async def remind_me(update: Update, context: CallbackContext) -> None:
    """Set a reminder based on the user's input."""
    try:
        # Parse time and message from the user's input
        time_str = context.args[0]
        message = " ".join(context.args[1:])
        
        # Convert time to minutes (example: 10m for 10 minutes)
        if time_str.endswith('m'):
            minutes = int(time_str[:-1])
            reminder_time = datetime.now() + timedelta(minutes=minutes)
        else:
            await update.message.reply_text("Invalid time format. Please use a format like '10m'.")
            return
        
        # Store the reminder
        reminders[update.message.chat_id] = {'time': reminder_time, 'message': message, 'status': 'Active'}
        
        await update.message.reply_text(f"Reminder set for {minutes} minutes from now: {message}")
    
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /remindme <time> <message> (e.g., /remindme 10m Take a break).")

# View tasks functionality
async def tasks(update: Update, context: CallbackContext) -> None:
    """Display all tasks."""
    tasks = "Your tasks:\n"
    if not reminders:
        tasks += "No tasks set."
    else:
        for chat_id, reminder in reminders.items():
            tasks += f"- {reminder['message']} (at {reminder['time'].strftime('%H:%M:%S')})\n"
    await update.message.reply_text(tasks)

# Add task functionality
async def add_task(update: Update, context: CallbackContext) -> None:
    """Add a new task to the task list."""
    task = " ".join(context.args)
    if not task:
        await update.message.reply_text("Usage: /addtask <task> (e.g., /addtask Finish project).")
        return
    reminders[update.message.chat_id] = {'time': datetime.now(), 'message': task, 'status': 'Active'}
    await update.message.reply_text(f"Task added: {task}")

# Status functionality
async def status(update: Update, context: CallbackContext) -> None:
    """Show current status of tasks and reminders."""
    status_message = "Current Status:\n"
    
    if not reminders:
        status_message += "No tasks or reminders set."
    else:
        for chat_id, reminder in reminders.items():
            reminder_status = reminder['status']
            status_message += f"- {reminder['message']} (at {reminder['time'].strftime('%H:%M:%S')}) - Status: {reminder_status}\n"
    
    await update.message.reply_text(status_message)

# Check reminders
async def check_reminders(context: CallbackContext) -> None:
    """Check if it's time for any reminders."""
    now = datetime.now()
    for chat_id, reminder in list(reminders.items()):
        if reminder['time'] <= now:
            await context.bot.send_message(chat_id, f"Reminder: {reminder['message']}")
            reminders[chat_id]['status'] = 'Completed'
            await context.bot.send_message(chat_id, f"Status: Reminder completed and marked as 'Completed'.")

# Main function to set up the bot
def main():
    # Replace 'YOUR_BOT_TOKEN' with your bot's token
    TELEGRAM_BOT_TOKEN = '8051492646:AAFRDsgyKT1YicuAb4d8DPxYWrXAwTUXRDk'

    # Create the Application and pass the bot token securely
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Register handlers for commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("remindme", remind_me))
    application.add_handler(CommandHandler("tasks", tasks))
    application.add_handler(CommandHandler("addtask", add_task))
    application.add_handler(CommandHandler("status", status))

    # Set up a job to check reminders every minute
    application.job_queue.run_repeating(check_reminders, interval=60, first=0)

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()
