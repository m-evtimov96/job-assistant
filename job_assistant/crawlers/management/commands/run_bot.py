from django.core.management.base import BaseCommand
import logging
import requests
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, filters, ApplicationBuilder, ContextTypes
from job_assistant.settings import BOT_TOKEN

# TODO: Move the bot logic to seperate file and only start the script from here
class Command(BaseCommand):
    help = "Run the telegram bot."

    def handle(self, *args, **options):

        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
        )

        # Django API URLs
        DJANGO_API_GET_CATEGORIES_URL = "http://127.0.0.1:8000/categories/"
        DJANGO_API_GET_TECHNOLOGIES_URL = "http://127.0.0.1:8000/technologies/"
        DJANGO_API_GET_WORKPLACES_URL = "http://127.0.0.1:8000/workplaces/"
        DJANGO_API_EDIT_CATEGORIES_URL = ""
        DJANGO_API_EDIT_TECHNOLOGIES_URL = ""
        DJANGO_API_EDIT_WORKPLACES_URL = ""

        # Command handlers

        async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            await update.message.reply_text("Welcome! Please use /search or /jobs to continue.")

        async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            keyboard = [
                [InlineKeyboardButton("Edit categories", callback_data='edit_categories')],
                [InlineKeyboardButton("Edit technologies", callback_data='edit_technologies')],
                [InlineKeyboardButton("Edit workplaces", callback_data='edit_workplaces')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text('Please choose which part of your search to edit.', reply_markup=reply_markup)

        async def handle_search_options(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            query = update.callback_query
            await query.answer()
            
            logging.info(f"Button clicked: {query.data}")

            if query.data == 'edit_categories':
                await query.message.reply_text("Provide categories separated by whitespaces:\nFor example: DevOps Frontend QA Python")
                context.user_data['edit_mode'] = 'categories'

            elif query.data == 'edit_technologies':
                await query.message.reply_text("Provide technologies separated by whitespaces:\nFor example: Django ElasticSearch Redis Jira")
                context.user_data['edit_mode'] = 'technologies'

            elif query.data == 'edit_workplaces':
                response = requests.get(DJANGO_API_GET_WORKPLACES_URL)
                workplaces = response.json()

                # Initialize selected workplaces in user_data if not already done
                selected_workplaces = context.user_data.get('selected_workplaces', [])

                # Create buttons with selection highlights
                keyboard = [
                    [InlineKeyboardButton(f"{workplace['name']}{' ✅' if workplace['id'] in selected_workplaces else ''}", callback_data=f"workplace_{workplace['id']}")]
                    for workplace in workplaces
                ]
                keyboard.append([InlineKeyboardButton("Save", callback_data='save_workplaces')])
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.message.reply_text('Select workplaces:', reply_markup=reply_markup)
                context.user_data['edit_mode'] = 'workplaces'

        async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            edit_mode = context.user_data.get('edit_mode')

            if edit_mode == 'categories':
                keywords = update.message.text
                response = requests.get(DJANGO_API_GET_CATEGORIES_URL, params={'search': keywords})
                categories = response.json()
                
                if categories:
                    category_names = [category['name'] for category in categories]
                    category_ids = [category['id'] for category in categories]
                    # TODO: Edit categories in search obj
                    # requests.post(DJANGO_API_EDIT_CATEGORIES_URL, json={'categories': category_ids})
                    
                    await update.message.reply_text(f"Search categories set to: {', '.join(category_names)}")
                else:
                    await update.message.reply_text("No categories found.")
                await search_command(update, context)

            elif edit_mode == 'technologies':
                keywords = update.message.text
                response = requests.get(DJANGO_API_GET_TECHNOLOGIES_URL, params={'search': keywords})
                technologies = response.json()
                
                if technologies:
                    technology_names = [tech['name'] for tech in technologies]
                    technology_ids = [tech['id'] for tech in technologies]
                    # TODO: Edit technologies in search obj
                    # requests.post(DJANGO_API_EDIT_TECHNOLOGIES_URL, json={'technologies': technology_ids})
                
                    await update.message.reply_text(f"Technologies found: {', '.join(technology_names)}")
                else:
                    await update.message.reply_text("No technologies found.")
                await search_command(update, context)

        async def save_workplaces(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            selected_workplaces = context.user_data.get('selected_workplaces', [])
            if selected_workplaces:
                response = requests.get(DJANGO_API_GET_WORKPLACES_URL)
                workplaces = response.json()
                workplace_names = [workplace['name'] for workplace in workplaces if workplace['id'] in selected_workplaces]
                # Send the selected workplaces to the API
                # requests.post(DJANGO_API_EDIT_WORKPLACES_URL, json={'workplaces': selected_workplaces})
                
                await update.callback_query.message.reply_text(f"You chose workplaces: {', '.join(workplace_names)}")
            else:
                await update.callback_query.message.reply_text("No workplaces selected.")
            # TODO: Fix this redirect to search command menu
            await search_command(update.callback_query.message, context)

        async def workplace_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            query = update.callback_query
            await query.answer()

            logging.info(f"Callback data in workplace_selection_handler: {query.data}")

            if query.data.startswith('workplace_'):
                workplace_id = int(query.data.split('_')[1])
                selected_workplaces = context.user_data.get('selected_workplaces', [])

                if workplace_id in selected_workplaces:
                    selected_workplaces.remove(workplace_id)  # Deselect if already selected
                else:
                    selected_workplaces.append(workplace_id)  # Select if not selected

                context.user_data['selected_workplaces'] = selected_workplaces
                
                response = requests.get(DJANGO_API_GET_WORKPLACES_URL)
                workplaces = response.json()

                keyboard = [
                    [InlineKeyboardButton(f"{workplace['name']}{' ✅' if workplace['id'] in selected_workplaces else ''}", callback_data=f"workplace_{workplace['id']}")]
                    for workplace in workplaces
                ]
                keyboard.append([InlineKeyboardButton("Save", callback_data='save_workplaces')])
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_reply_markup(reply_markup=reply_markup)

            elif query.data == 'save_workplaces':
                await save_workplaces(update, context)

        application = ApplicationBuilder().token(BOT_TOKEN).build()

        # Register handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("search", search_command))
        application.add_handler(CallbackQueryHandler(handle_search_options, pattern='^(edit_categories|edit_technologies|edit_workplaces)$'))
        application.add_handler(CallbackQueryHandler(workplace_selection_handler, pattern='^(workplace_.*|save_workplaces)$'))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

        application.run_polling()