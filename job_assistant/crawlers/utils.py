import html
from job_assistant.crawlers.models import Category

def handle_categories(ad):
    category_names = ad.pop("categories")
    categories = []
    for name in category_names:
        category, created = Category.objects.get_or_create(name=name.strip())
        categories.append(category)
    return categories

def clean_body(ad, cleaner):
    body = cleaner.clean(ad["body"])
    body = html.unescape(body)
    ad["body"] = body