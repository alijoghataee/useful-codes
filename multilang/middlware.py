from django.utils import translation

from app import settings


class CustomLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'):
            return self.get_response(request)

        language_code = request.GET.get('lang')
        if not language_code:
            language_code = settings.DEFAULT_WORKING_LANGUAGE
        translation.activate(language_code)
        request.LANGUAGE_CODE = language_code

        response = self.get_response(request)
        translation.deactivate()

        return response
