from django.apps import AppConfig

class UsersConfig(AppConfig):
    name = 'geeksurvey'

    def ready(self):
        import geeksurvey.signals
