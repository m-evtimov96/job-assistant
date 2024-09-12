# Job-Assistant
Job-Assistant is a project designed to automate job searching and application management by utilizing web scraping techniques and interacting through a Telegram bot. It enables users to create profiles, search for jobs, and receive job listings in real time. The backend of the project is built using Django Rest Framework (DRF), and job listings are scraped from websites like dev.bg using custom spiders. This project is part of my Masters Thesis.

## 1. Features
- User Profiles
Users can create and manage their profiles, including information such as job preferences, skills, and desired location.
Each user has one profile, but future updates aim to allow multiple profiles.
Profiles are used to tailor job searches to the user's preferences.
- Job Search
Users can search for jobs directly through the Telegram bot.
Jobs are scraped from websites like dev.bg, and users receive listings matching their profile preferences.
Users can set search filters to refine results.
- Job Ad Representation
Job ads are presented within the Telegram chat, displaying key details such as job title, company, location, and a brief description.
Below each job ad, users have two buttons:
Add to Favorites: Save the job listing for later reference.
Generate CV: Automatically generate a CV based on the user's profile to apply for the job.
- Favorites Management
Users can mark job ads as favorites and view a list of all saved jobs.
This allows easy access to jobs they are interested in or plan to apply to.
- CV Generation
The bot provides functionality to automatically generate a CV based on the user's profile.
The generated CV can be used directly to apply for jobs.

## 2. Technologies Used
**Python**: The core language for backend development.\
**Django Rest Framework (DRF)**: Provides the API for managing user profiles, job searches, and other bot functionalities.\
**Telegram Bot API**: Used to handle user interactions and present job listings in a chat format.\
**Celery**: For background tasks such as scraping job ads from websites and sending notifications.\
**PostgreSQL**: Database for storing user profiles, job ads, and other data.\
**Scrapy**: A web scraping framework used to collect job listings from external websites like dev.bg.

## 3. Architecture
The Job-Assistant project is designed around four key components: Django, Django Rest Framework (DRF), Scrapy, and the Telegram Bot API. Each of these plays a crucial role in the system, allowing users to interact with job data scraped from external websites. Here's how they work together:

1. **Django as the Core Backend**\
Django provides the foundation for managing the database, user authentication, and overall web application logic. It handles storing job listings, user profiles, and favorites.
The Django Admin Panel allows admins to manage users, jobs, and settings.
2. **Django Rest Framework (DRF) API**\
DRF acts as the bridge between the Django backend and the Telegram bot, exposing endpoints for actions like profile management, job searches, and scraping.
DRF is the intermediary between the bot and the job data, allowing the bot to send requests and receive responses via the API.
3. **Scrapy for Web Scraping**\
Scrapy is the web scraping framework used to gather job listings from external websites like dev.bg. It automates the process of sending requests, extracting data, and storing the results.
A Scrapy Spider is specifically designed to crawl and scrape job data from the target website. It navigates the website's HTML structure, identifies job details (such as title, description, salary, and location), and sends the extracted data to Django for further processing.
How Scrapy Works in the Project:
The Scrapy Spider runs periodically, scraping job data from the designated website.
Once the job data is scraped, it is processed and stored in the database.
This scraped data becomes accessible via the DRF API, allowing both the Telegram Bot and other systems (such as future web apps) to access fresh job listings.
4. **Telegram Bot API**\
Telegram Bot is the user-facing component that allows users to interact with the project. Users can request job listings, add them to favorites, or generate CVs using simple commands.
The bot interacts with the DRF API, retrieving job listings or performing actions based on user commands, and sends responses back to users on Telegram.
5. **Celery for Background Tasks**\
Celery is used to schedule and run the Scrapy spider at regular intervals, ensuring that job listings are updated automatically.
This allows the bot and API to serve the latest job data to users without manual intervention.

## 4. Installation
*Before starting the installation you will need an empty postgreSQL db and installed redis and celery*\
Clone the repository:
```
git clone https://github.com/m-evtimov96/job-assistant.git
cd job-assistant
```
### 1. Set up a virtual environment and install dependencies:
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
### 2. Run migrations:
```
python manage.py migrate
```
### 3. Add the env vars (using sample.env)
### 4. Run the development server:
```
python manage.py runserver
```
### 5. Set up Celery (for background tasks):
```
celery -A job_assistant worker --loglevel=info
```
### 6. Set up the Telegram bot:

### 7. Follow the official Telegram Bot API documentation to create a bot and obtain a token.
Set the token in your environment variables.

## 5. Roadmap & Future Improvements
- Multiple User Profiles: Allow users to create and switch between multiple profiles to search for jobs in different fields or locations.\
- Support for More Job Websites: Add spiders for more job websites to expand the range of available job ads.\
- Graceful Handling of Dynamic Content: Improve scraping capabilities to handle dynamically generated content.\
- Web Application: Develop a web-based interface that uses the same API, providing an alternative to the Telegram bot.\
- API Authentication: Implement token-based authentication (e.g., JWT) to secure the DRF API.\
- Deployment: Deploy the bot so it is publicly available for all Telegram users.\

## 6. Contact
About improvement ideas, bugs or everything else contact me here or via email.
