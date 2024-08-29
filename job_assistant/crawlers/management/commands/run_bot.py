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
        # TODO: Mby return to the /jobs list when receiving job ads and viewing/removing favourites
        # TODO: Add option for generating CV's for a job ad using the profile data and ChatGPT - button in add repr

        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
        )

        # Django API URLs
        DJANGO_API_GET_CATEGORIES_URL = "http://127.0.0.1:8000/categories/"
        DJANGO_API_GET_TECHNOLOGIES_URL = "http://127.0.0.1:8000/technologies/"
        DJANGO_API_GET_WORKPLACES_URL = "http://127.0.0.1:8000/workplaces/"
        DJANGO_API_SEARCH_URL = "http://127.0.0.1:8000/searches/"
        DJANGO_API_GET_JOB_ADS_URL = "http://127.0.0.1:8000/job-ads/"
        DJANGO_API_PROFILE_URL = "http://127.0.0.1:8000/profiles/"
        DJANGO_API_FAVOURITES_URL = "http://127.0.0.1:8000/favourites/"

        # Base handlers
        ###############
        async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            await update.message.reply_text("Welcome! Please use /search, /jobs or /profile to continue.")

        async def unified_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            if 'job_search_mode' in context.user_data:
                await job_message_handler(update, context)
            elif 'edit_mode' in context.user_data:
                await search_message_handler(update, context)
            elif 'profile_mode' in context.user_data:
                await profile_message_handler(update, context)


        # Help functions
        ################
        def clear_user_data(data):
            data.pop("job_search_mode", None)
            data.pop("edit_mode", None)

        def shorten_profile_data(data):
            data = (data[:500] + '...') if len(data) > 500 else data
            return data


        # Search handlers
        #################
        async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            keyboard = [
                [InlineKeyboardButton("View current search parameters", callback_data='view_search_parameters')],
                [InlineKeyboardButton("Edit categories", callback_data='edit_categories')],
                [InlineKeyboardButton("Edit technologies", callback_data='edit_technologies')],
                [InlineKeyboardButton("Edit workplaces", callback_data='edit_workplaces')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            if update.message:
                await update.message.reply_text('Choose what to do with your personal search.', reply_markup=reply_markup)
            elif update.callback_query:
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
                clear_user_data(context.user_data)
                context.user_data['edit_mode'] = 'categories'

            elif query.data == 'edit_technologies':
                await query.message.reply_text("Provide technologies separated by whitespaces:\nFor example: Django ElasticSearch Redis Jira")
                clear_user_data(context.user_data)
                context.user_data['edit_mode'] = 'technologies'

            elif query.data == 'edit_workplaces':
                response = requests.get(DJANGO_API_GET_WORKPLACES_URL)
                workplaces = response.json().get("results")

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

        async def search_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            edit_mode = context.user_data.get('edit_mode')
            user_id = update.effective_user.id

            if edit_mode == 'categories':
                keywords = update.message.text
                response = requests.get(DJANGO_API_GET_CATEGORIES_URL, params={'search': keywords})
                categories = response.json().get("results", None)
                
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
                technologies = response.json().get("results", None)
                
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
                workplaces = response.json().get("results", [])

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
                        workplaces = requests.get(DJANGO_API_GET_WORKPLACES_URL).json().get("results")
                        workplace_names = [workplace['name'] for workplace in workplaces if workplace['id'] in selected_workplaces]
                        await query.message.reply_text(f"Search workplaces set to: {', '.join(workplace_names)}")
                    else:
                        await query.message.reply_text("Search workplaces reset to all.")
                else:
                    await query.message.reply_text("No workplaces selected.")
                await search_command(update.callback_query, context)

        
        # Jobs handlers
        ###############
        async def jobs_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            keyboard = [
                [InlineKeyboardButton("Latest job ads", callback_data='last_n_job_ads')],
                [InlineKeyboardButton("Quick search", callback_data='quick_search')],
                [InlineKeyboardButton("View Favourites", callback_data='view_favourites')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if update.message:
                await update.message.reply_text(
                    "Please choose an option to search for job ads.\nThe 'latest job ads' function uses your predefined search, "
                    "while the 'quick search' does a full text search in the title and body of the ads with provided keywords.",
                    reply_markup=reply_markup
                )
            elif update.callback_query:
                await update.callback_query.message.reply_text(
                    "Please choose an option to search for job ads.\nThe 'latest job ads' function uses your predefined search, "
                    "while the 'quick search' does a full text search in the title and body of the ads with provided keywords.",
                    reply_markup=reply_markup
                )

        async def handle_jobs_options(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            query = update.callback_query
            await query.answer()

            if query.data == 'last_n_job_ads':
                response = requests.get(DJANGO_API_SEARCH_URL + str(update.effective_user.id) + "/")
                if response.status_code == 404:
                    await query.message.reply_text("No search configuration found. Please set up your search parameters first.")
                    return
                await query.message.reply_text("How many job ads tied to your personal search would you like to see? (1-20)")
                context.user_data['job_search_mode'] = 'last_n_job_ads'
            
            elif query.data == 'quick_search':
                await query.message.reply_text("Please provide one or multiple search keywords for the full text search.\nFor example: Python AI")
                context.user_data['job_search_mode'] = 'quick_search'

            elif query.data == 'view_favourites':
                user_id = update.effective_user.id
                favourites_response = requests.get(DJANGO_API_FAVOURITES_URL, params={"user": user_id})
                if favourites_response.status_code == 200:
                    favourite_jobs = favourites_response.json().get('results', [])
                    if favourite_jobs:
                        job_ids = [job['job_ad'] for job in favourite_jobs]
                        jobs_response = requests.get(DJANGO_API_GET_JOB_ADS_URL, params={"id": ','.join(map(str, job_ids))})
                        job_ads = jobs_response.json().get("results", [])
                        await display_job_ads(update, job_ads, favourite_mode=True)
                    else:
                        await query.message.reply_text("You have no favourite job ads.")
                else:
                    await query.message.reply_text("Failed to retrieve your favourite job ads.")

        async def job_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            user_id = update.effective_user.id
            job_search_mode = context.user_data.get('job_search_mode')
            
            if job_search_mode == 'last_n_job_ads':
                try:
                    limit = int(update.message.text)
                    if 1 <= limit <= 20:
                        search_data = requests.get(DJANGO_API_SEARCH_URL + f"{user_id}/").json()
                        categories = json.loads(search_data.get('categories', '[]') or '[]')
                        technologies = json.loads(search_data.get('technologies', '[]') or '[]')
                        workplaces = json.loads(search_data.get('workplaces', '[]') or '[]')

                        params = []
                        if categories:
                            params.append(f'categories={",".join(map(str, categories))}')
                        if technologies:
                            params.append(f'technologies={",".join(map(str, technologies))}')
                        if workplaces:
                            params.append(f'workplace={",".join(map(str, workplaces))}')
                        params.append(f'limit={limit}')

                        query_string = '&'.join(params)
                        response = requests.get(f"{DJANGO_API_GET_JOB_ADS_URL}?{query_string}").json()
                        job_ads = response.get("results", None)

                        await display_job_ads(update, job_ads)
                    else:
                        await update.message.reply_text("Please enter a number between 1 and 20.")
                except ValueError:
                    await update.message.reply_text("Please enter a valid number.")
            
            elif job_search_mode == 'quick_search':
                search_term = update.message.text
                await update.message.reply_text("How many job ads would you like to see? (1-20)")
                context.user_data['quick_search_term'] = search_term
                context.user_data['job_search_mode'] = 'quick_search_limit'

            elif job_search_mode == 'quick_search_limit':
                try:
                    limit = int(update.message.text)
                    if 1 <= limit <= 20:
                        search_term = context.user_data.get('quick_search_term')
                        response = requests.get(DJANGO_API_GET_JOB_ADS_URL, params={"search": search_term, "limit": limit}).json()
                        job_ads = response.get("results", None)
                        await display_job_ads(update, job_ads)
                    else:
                        await update.message.reply_text("Please enter a number between 1 and 20.")
                except ValueError:
                    await update.message.reply_text("Please enter a valid number.")

        async def display_job_ads(update: Update, job_ads: list, favourite_mode: bool = False) -> None:
            if not job_ads:
                await update.message.reply_text("No job ads found. Try to modify your search criteria.")
                return

            if favourite_mode:
                await update.callback_query.message.reply_text("Here are your favourite job ads:")
            else:
                await update.message.reply_text("Here are the job ads that match your search criteria:")

            for ad in job_ads:
                job_id = ad.get("id")
                title = ad.get("title", "N/A")
                company = ad.get("company", "N/A")
                workplace = ad.get("workplace", "N/A")
                date = ad.get("date", "N/A")
                categories = ", ".join(ad.get("categories", [])) or "N/A"
                technologies = ", ".join(ad.get("technologies", [])) or "N/A"
                url = ad.get("url", "#")

                message = (
                    f"<b>{title}</b>\n"
                    f"Company: {company}\n"
                    f"Location: {workplace}\n"
                    f"Date: {date}\n"
                    f"Categories: {categories}\n"
                    f"Technologies: {technologies}\n"
                    f"{url}"
                )
                
                check_data = {"user": update.effective_user.id, "job_ad": job_id}
                check_response = requests.get(DJANGO_API_FAVOURITES_URL, params=check_data)
                is_favourite = check_response.json().get("count", 0) > 0

                if favourite_mode or is_favourite:
                    button_text = "Remove from Favourites"
                    callback_data = f'remove_favourite_{job_id}'
                else:
                    button_text = "Add to Favourites"
                    callback_data = f'add_favourite_{job_id}'

                keyboard = [
                    [InlineKeyboardButton(button_text, callback_data=callback_data)],
                    [InlineKeyboardButton("Generate CV", callback_data=f'generate_cv_{job_id}')],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                if update.message:
                    await update.message.reply_text(message, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
                elif update.callback_query:
                    await update.callback_query.message.reply_text(message, parse_mode=ParseMode.HTML, reply_markup=reply_markup)

        async def handle_job_ad_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            query = update.callback_query
            await query.answer()
            user_id = update.effective_user.id

            if query.data.startswith('add_favourite_'):
                job_id = int(query.data.split('add_favourite_')[1])
                check_data = {"user": user_id, "job_ad": job_id}

                result = requests.get(DJANGO_API_FAVOURITES_URL, params=check_data).json()
                if result["count"] == 0:
                    add_data = {"user": user_id, "job_ad": job_id}
                    add_response = requests.post(DJANGO_API_FAVOURITES_URL, json=add_data)

                    if add_response.status_code == 201:
                        await query.message.reply_text("The job ad was added to your favourites!")
                    else:
                        await query.message.reply_text("Failed to add the job ad to your favourites.")
                else:
                    await query.message.reply_text("This job ad is already in your favourites.")

            elif query.data.startswith('remove_favourite_'):
                job_id = int(query.data.split('remove_favourite_')[1])

                check_data = {"user": user_id, "job_ad": job_id}
                result = requests.get(DJANGO_API_FAVOURITES_URL, params=check_data).json()

                if result["count"] > 0:
                    favourite_id = result['results'][0]['id']
                    delete_response = requests.delete(f"{DJANGO_API_FAVOURITES_URL}{favourite_id}/")

                    if delete_response.status_code == 204:
                        await query.message.reply_text("The job ad was removed from your favourites.")
                    else:
                        await query.message.reply_text("Failed to remove the job ad from your favourites.")
                else:
                    await query.message.reply_text("This job ad is not in your favourites.")

            elif query.data.startswith('generate_cv_'):
                job_id = query.data.split('generate_cv_')[1]

                # Logic to generate a CV tailored to the job
                # cv_link = generate_cv_for_job(user_id, job_id)
                await query.message.reply_text(f"Your CV has been generated! You can download it here:")

        # Profile handlers
        ##################
        MAX_LENGTHS = {
            'bio': 1000,
            'education': 1000,
            'work_experience': 3900,
            'skills': 2000,
            'other': 4000
        }

        async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            keyboard = [
                [InlineKeyboardButton("View Profile", callback_data='view_profile')],
                [InlineKeyboardButton("Edit Bio", callback_data='edit_bio')],
                [InlineKeyboardButton("Edit Education", callback_data='edit_education')],
                [InlineKeyboardButton("Edit Work Experience", callback_data='edit_work_experience')],
                [InlineKeyboardButton("Edit Skills", callback_data='edit_skills')],
                [InlineKeyboardButton("Edit Other", callback_data='edit_other')],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            if update.message:
                await update.message.reply_text('Choose what to do with your profile information.', reply_markup=reply_markup)
            elif update.callback_query:
                await update.callback_query.message.reply_text('Choose what to do with your profile information.', reply_markup=reply_markup)

        async def handle_profile_options(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            query = update.callback_query
            await query.answer()

            if query.data == 'view_profile':
                user_id = update.effective_user.id
                response = requests.get(DJANGO_API_PROFILE_URL + str(user_id) + "/")
                if response.status_code == 200:
                    profile_data = response.json()
                    bio = shorten_profile_data(profile_data.get('bio') or 'No information')
                    education = shorten_profile_data(profile_data.get('education') or 'No information')
                    work_experience = shorten_profile_data(profile_data.get('work_experience') or 'No information')
                    skills = shorten_profile_data(profile_data.get('skills') or 'No information')
                    other = shorten_profile_data(profile_data.get('other') or 'No information')

                    profile_message = (
                        f"<b>Profile Information</b>\n"
                        f"<b>Bio:</b> {bio}\n"
                        f"<b>Education:</b> {education}\n"
                        f"<b>Work Experience:</b> {work_experience}\n"
                        f"<b>Skills:</b> {skills}\n"
                        f"<b>Other:</b> {other}\n"
                    )
                    await query.message.reply_text(profile_message, parse_mode=ParseMode.HTML)
                else:
                    await query.message.reply_text("No profile found. Please add your profile information first.")
            
            else:
                split_place = query.data.count("_")+1
                mode = query.data.split('_')[1:split_place]
                mode = "_".join(mode)
                await query.message.reply_text(f"Please provide information for {mode.replace('_', ' ')} section. (max chars - {MAX_LENGTHS.get(mode, 3900)})")
                clear_user_data(context.user_data)
                context.user_data['profile_mode'] = mode

        async def profile_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            profile_mode = context.user_data.get('profile_mode')
            user_id = update.effective_user.id

            
            user_input = update.message.text
            max_length = MAX_LENGTHS.get(profile_mode, 3900)
            truncated_input = user_input[:max_length]
            data = {
                profile_mode: truncated_input
            }

            response = requests.get(DJANGO_API_PROFILE_URL + str(user_id) + "/")
            if response.status_code == 200:
                requests.patch(DJANGO_API_PROFILE_URL + str(user_id) + "/", data=data)
            else:
                data["user"] = user_id
                requests.post(DJANGO_API_PROFILE_URL, data=data)

            if len(user_input) > max_length:
                await update.message.reply_text(f"Your {profile_mode.replace('_', ' ')} information was too long and has been truncated to {max_length} characters.")
            else:
                await update.message.reply_text(f"Your {profile_mode.replace('_', ' ')} information has been updated.")

            await profile_command(update, context)


        # Application setup and start
        #############################
        application = ApplicationBuilder().token(BOT_TOKEN).build()

        start_handler = CommandHandler("start", start)
        base_message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, unified_message_handler)
        base_handlers = [
            start_handler,
            base_message_handler,
        ]

        search_menu_handler = CommandHandler("search", search_command)
        search_options_handler = CallbackQueryHandler(handle_search_options, pattern='^(view_search_parameters|edit_categories|edit_technologies|edit_workplaces)$')
        search_workplace_handler = CallbackQueryHandler(workplace_selection_handler, pattern='^(workplace_.*|save_workplaces)$')
        search_handlers = [
            search_menu_handler,
            search_options_handler,
            search_workplace_handler,   
        ]

        jobs_menu_handler = CommandHandler("jobs", jobs_command)
        jobs_search_options_handler = CallbackQueryHandler(handle_jobs_options, pattern='^(last_n_job_ads|quick_search|view_favourites)$')
        jobs_buttons_handler = CallbackQueryHandler(handle_job_ad_buttons)
        jobs_handlers = [
            jobs_menu_handler,
            jobs_search_options_handler,
            jobs_buttons_handler,
        ]


        profile_menu_handler = CommandHandler("profile", profile_command)
        profile_options_handler = CallbackQueryHandler(handle_profile_options, pattern='^(view_profile|edit_bio|edit_education|edit_work_experience|edit_skills|edit_other)$')
        profile_handlers = [
            profile_menu_handler,
            profile_options_handler,
        ]

        handlers = base_handlers + search_handlers + jobs_handlers + profile_handlers
        application.add_handlers(handlers)

        application.run_polling()
