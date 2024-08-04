from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name


class JobAd(models.Model):
    title = models.CharField(max_length=100)
    body = models.TextField()
    date = models.DateField()
    company = models.CharField(max_length=50)
    categories = models.ManyToManyField(Category)
    workplace = models.CharField(max_length=50)
    url = models.URLField()
