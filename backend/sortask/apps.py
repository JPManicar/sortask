from django.apps import AppConfig


class SortaskConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sortask'

    def ready(self):
        import sortask.signals
