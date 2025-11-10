from django.db import models

from core import settings
from multilang.managers import LanguageModelManager


class LanguageModel(models.Model):
    language_code = models.CharField(max_length=10, choices=settings.WORKING_LANGUAGES,
                                     default=settings.DEFAULT_WORKING_LANGUAGE)

    objects = LanguageModelManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True
