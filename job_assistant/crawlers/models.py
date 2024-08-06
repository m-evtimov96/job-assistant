from django.db import models
from job_assistant.crawlers.managers import SoftDeleteManager

class Category(models.Model):
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
    workplace = models.CharField(max_length=100) # TODO: Mby rework this to be Fk with separate model
    url = models.URLField()
