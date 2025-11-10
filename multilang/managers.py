from django.db import models
from django.utils import translation

from app import settings



class LanguageAwareQuerySet(models.QuerySet):
    """
        A QuerySet that automatically filters objects by the current active language.

    Why:
        In Django, querysets defined at the class level are evaluated once,
        before the request and its language are set. This causes filtering
        by language_code to use the default language always.

    What it does:
        This QuerySet delays adding the language filter until the last moment
        (just before the database query runs). It reads the current active
        language from Django’s translation system and injects the filter
        dynamically.

    How it helps:
        Allows querysets to be defined early (e.g., as class attributes) but
        still respect the user's selected language at runtime without
        requiring changes in every view or query.
    """
    def _fetch_all(self):
        self._apply_language_filter()
        return super()._fetch_all()

    def _apply_language_filter(self):
        if not hasattr(self, '_language_filtered'):
            valid_lang_codes = [code for code, _ in settings.WORKING_LANGUAGES]
            lang_code = translation.get_language()
            if lang_code not in valid_lang_codes:
                lang_code = settings.DEFAULT_WORKING_LANGUAGE
            self.query.add_q(models.Q(language_code=lang_code))
            self._language_filtered = True


class LanguageModelManager(models.Manager):
    def get_queryset(self):
        return LanguageAwareQuerySet(self.model, using=self._db)

    def create(self, **kwargs):
        valid_lang_codes = [code for code, _ in settings.WORKING_LANGUAGES]
        lang_code = translation.get_language() if translation.get_language() in valid_lang_codes else settings.DEFAULT_WORKING_LANGUAGE
        kwargs.setdefault('language_code', lang_code)
        return super().create(**kwargs)

    def bulk_create(self, objs, **kwargs):
        valid_lang_codes = [code for code, _ in settings.WORKING_LANGUAGES]
        lang_code = translation.get_language() if translation.get_language() in valid_lang_codes else settings.DEFAULT_WORKING_LANGUAGE
        for obj in objs:
            if not getattr(obj, 'language_code', None):
                obj.language_code = lang_code
        return super().bulk_create(objs, **kwargs)
