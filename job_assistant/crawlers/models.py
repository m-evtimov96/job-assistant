from django.db import models

class JobAd(models.Model):
    title = models.CharField(max_length=100)
    body = models.TextField()
    date = models.DateField()
    company = models.CharField(max_length=50)
    categories = models.CharField(max_length=150)
    url = models.URLField()
