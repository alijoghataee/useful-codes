from unfold.admin import ModelAdmin


class LanguageModelAdmin(ModelAdmin):
    list_filter = ['language_code']

    def get_queryset(self, request):
        return self.model.all_objects.get_queryset()
