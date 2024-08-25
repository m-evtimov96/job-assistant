from django.core.management.base import BaseCommand
import logging
import requests
import json
from telegram.constants import ParseMode
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
        DJANGO_API_SEARCH_URL = "http://127.0.0.1:8000/searches/"
        DJANGO_API_EDIT_CATEGORIES_URL = ""
        DJANGO_API_EDIT_TECHNOLOGIES_URL = ""
        DJANGO_API_EDIT_WORKPLACES_URL = ""

        # Command handlers

        async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            await update.message.reply_text("Welcome! Please use /search or /jobs to continue.")

        async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            keyboard = [
                [InlineKeyboardButton("View current search parameters", callback_data='view_search_parameters')],
                [InlineKeyboardButton("Edit categories", callback_data='edit_categories')],
                [InlineKeyboardButton("Edit technologies", callback_data='edit_technologies')],
                [InlineKeyboardButton("Edit workplaces", callback_data='edit_workplaces')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            if update.message:  # Direct message case
                await update.message.reply_text('Choose what to do with your personal search.', reply_markup=reply_markup)
            elif update.callback_query:  # Callback query case
                await update.callback_query.message.reply_text('Choose what to do with your personal search.', reply_markup=reply_markup)

        async def handle_search_options(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            query = update.callback_query
            await query.answer()

            if query.data == 'view_search_parameters':
                user_id = update.effective_user.id
                response = requests.get(DJANGO_API_SEARCH_URL + str(user_id) + "/")
                if response.status_code == 200:
                    search_data = response.json()

                    categories = json.loads(search_data.get('categories', '[]') or '[]')
                    technologies = json.loads(search_data.get('technologies', '[]') or '[]')
                    workplaces = json.loads(search_data.get('workplaces', '[]') or '[]')

                    category_names = ", ".join([requests.get(DJANGO_API_GET_CATEGORIES_URL + f"{category_id}/").json()['name'] for category_id in categories])
                    technology_names = ", ".join([requests.get(DJANGO_API_GET_TECHNOLOGIES_URL + f"{tech_id}/").json()['name'] for tech_id in technologies])
                    workplace_names = ", ".join([requests.get(DJANGO_API_GET_WORKPLACES_URL + f"{workplace_id}/").json()['name'] for workplace_id in workplaces])

                    search_params_message = (
                            f"Current Search Parameters\n"
                            f"<b>Categories:</b> {category_names or 'None selected'}\n"
                            f"<b>Technologies:</b> {technology_names or 'None selected'}\n"
                            f"<b>Workplaces:</b> {workplace_names or 'None selected'}\n"
                        )
                    await query.message.reply_text(search_params_message, parse_mode=ParseMode.HTML)
                else:
                    await query.message.reply_text("No search configured yet. Please edit the search options first.")
            
            elif query.data == 'edit_categories':
                await query.message.reply_text("Provide categories separated by whitespaces:\nFor example: DevOps Frontend QA Python")
                context.user_data['edit_mode'] = 'categories'

            elif query.data == 'edit_technologies':
                await query.message.reply_text("Provide technologies separated by whitespaces:\nFor example: Django ElasticSearch Redis Jira")
                context.user_data['edit_mode'] = 'technologies'

            elif query.data == 'edit_workplaces':
                response = requests.get(DJANGO_API_GET_WORKPLACES_URL)
                workplaces = response.json()

                selected_workplaces = context.user_data.get('selected_workplaces', [])

                keyboard = [
                    [InlineKeyboardButton(f"{workplace['name']}{' ✅' if workplace['id'] in selected_workplaces else ''}", callback_data=f"workplace_{workplace['id']}")]
                    for workplace in workplaces
                ]
                keyboard.append([InlineKeyboardButton("All", callback_data='workplace_all')])
                keyboard.append([InlineKeyboardButton("Save", callback_data='save_workplaces')])
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.message.reply_text('Select workplaces:', reply_markup=reply_markup)
                context.user_data['edit_mode'] = 'workplaces'

        async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            edit_mode = context.user_data.get('edit_mode')
            user_id = update.effective_user.id

            if edit_mode == 'categories':
                keywords = update.message.text
                response = requests.get(DJANGO_API_GET_CATEGORIES_URL, params={'search': keywords})
                categories = response.json()
                
                if categories:
                    category_names = [category['name'] for category in categories]
                    category_ids = [category['id'] for category in categories]
                    search = requests.get(DJANGO_API_SEARCH_URL+str(user_id)+"/")
                    if search.status_code == 200:
                        data = {
                            "categories": f"{category_ids}"
                        }
                        requests.patch(DJANGO_API_SEARCH_URL+str(user_id)+"/", data=data)
                    else:
                        data = {
                            "user": user_id,
                            "categories": f"{category_ids}"
                        }
                        requests.post(DJANGO_API_SEARCH_URL, data=data)

                    await update.message.reply_text(f"Search categories set to: {', '.join(category_names)}")
                else:
                    await update.message.reply_text("No categories found. Please try again.")
                await search_command(update, context)

            elif edit_mode == 'technologies':
                keywords = update.message.text
                response = requests.get(DJANGO_API_GET_TECHNOLOGIES_URL, params={'search': keywords})
                technologies = response.json()
                
                if technologies:
                    technology_names = [tech['name'] for tech in technologies]
                    technology_ids = [tech['id'] for tech in technologies]
                    search = requests.get(DJANGO_API_SEARCH_URL+str(user_id)+"/")
                    if search.status_code == 200:
                        data = {
                            "technologies": f"{technology_ids}"
                        }
                        requests.patch(DJANGO_API_SEARCH_URL+str(user_id)+"/", data=data)
                    else:
                        data = {
                            "user": user_id,
                            "categories": f"{technology_ids}"
                        }
                        requests.post(DJANGO_API_SEARCH_URL, data=data)

                
                    await update.message.reply_text(f"Search technologies set to: {', '.join(technology_names)}")
                else:
                    await update.message.reply_text("No technologies found. Please try again.")
                await search_command(update, context)

        async def workplace_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            query = update.callback_query
            await query.answer()

            if query.data.startswith('workplace_'):
                if query.data != "workplace_all":
                    workplace_id = int(query.data.split('_')[1])
                    selected_workplaces = context.user_data.get('selected_workplaces', [])

                    if workplace_id in selected_workplaces:
                        selected_workplaces.remove(workplace_id)
                    else:
                        selected_workplaces.append(workplace_id)
                else:
                    selected_workplaces = []
                context.user_data['selected_workplaces'] = selected_workplaces
                
                response = requests.get(DJANGO_API_GET_WORKPLACES_URL)
                workplaces = response.json()

                keyboard = [
                    [InlineKeyboardButton(f"{workplace['name']}{' ✅' if workplace['id'] in selected_workplaces else ''}", callback_data=f"workplace_{workplace['id']}")]
                    for workplace in workplaces
                ]
                keyboard.append([InlineKeyboardButton(f"All{' ✅' if not selected_workplaces else ''}", callback_data='workplace_all')])
                keyboard.append([InlineKeyboardButton("Save", callback_data='save_workplaces')])
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_reply_markup(reply_markup=reply_markup)

            elif query.data == 'save_workplaces':
                selected_workplaces = context.user_data.get('selected_workplaces', "")
                if not selected_workplaces:
                    selected_workplaces = ""
                user_id = update.effective_user.id

                if selected_workplaces is not None:
                    search = requests.get(DJANGO_API_SEARCH_URL + str(user_id) + "/")
                    if search.status_code == 200:
                        data = {
                            "workplaces": f"{selected_workplaces}"
                        }
                        requests.patch(DJANGO_API_SEARCH_URL + str(user_id) + "/", data=data)
                    else:
                        data = {
                            "user": user_id,
                            "workplaces": f"{selected_workplaces}"
                        }
                        requests.post(DJANGO_API_SEARCH_URL, data=data)
                    if selected_workplaces:
                        workplaces = requests.get(DJANGO_API_GET_WORKPLACES_URL).json()
                        workplace_names = [workplace['name'] for workplace in workplaces if workplace['id'] in selected_workplaces]
                        await query.message.reply_text(f"Search workplaces set to: {', '.join(workplace_names)}")
                    else:
                        await query.message.reply_text("Search workplaces reset to all.")
                else:
                    await query.message.reply_text("No workplaces selected.")
                await search_command(update.callback_query, context)

        application = ApplicationBuilder().token(BOT_TOKEN).build()

        # Register handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("search", search_command))
        application.add_handler(CallbackQueryHandler(handle_search_options, pattern='^(view_search_parameters|edit_categories|edit_technologies|edit_workplaces)$'))
        application.add_handler(CallbackQueryHandler(workplace_selection_handler, pattern='^(workplace_.*|save_workplaces)$'))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

        application.run_polling()