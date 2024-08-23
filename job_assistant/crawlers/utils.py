import html
from job_assistant.crawlers.models import Category, Technology


# TODO: Rewrite this to single func, because its the same
def handle_categories(ad):
    category_names = ad.pop("categories")
    categories = []
    for name in category_names:
        category, created = Category.objects.get_or_create(name=name.strip())
        categories.append(category)
    return categories

def handle_technologies(ad):
    technology_names = ad.pop("technologies")
    technologies = []
    for name in technology_names:
        technology, created = Technology.objects.get_or_create(name=name.strip())
        technologies.append(technology)
    return technologies

def clean_body(ad, cleaner):
    body = cleaner.clean(ad["body"])
    body = html.unescape(body)
    ad["body"] = body