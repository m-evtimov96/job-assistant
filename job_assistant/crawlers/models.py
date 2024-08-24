from django.db import models
from job_assistant.crawlers.managers import SoftDeleteManager

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name


class Technology(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name


class Workplace(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name


class SoftDeleteModel(models.Model):
    """Soft delete model which hides the objects instead of deleting them"""

    is_deleted = models.BooleanField(default=False)
    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def delete(self):
        self.is_deleted = True
        self.save()

    def restore(self):
        self.is_deleted = False
        self.save()


class JobAd(SoftDeleteModel):
    title = models.CharField(max_length=150)
    body = models.TextField()
    date = models.DateField()
    company = models.CharField(max_length=100)
    categories = models.ManyToManyField(Category)
    technologies = models.ManyToManyField(Technology)
    workplace = models.ForeignKey(Workplace, on_delete=models.DO_NOTHING)
    url = models.URLField() #Mby make this unique


class Search(models.Model):
    user = models.IntegerField()
    categories = models.CharField(blank=True, null=True)
    techstack = models.CharField(blank=True, null=True)
    workplace = models.CharField(blank=True, null=True)
