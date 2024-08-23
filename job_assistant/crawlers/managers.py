from django.db import models


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(model=self.model, using=self._db).filter(is_deleted=False)

class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        self.update(is_deleted=True)
