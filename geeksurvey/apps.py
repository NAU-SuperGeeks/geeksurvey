from django.apps import AppConfig

class GeekSurveyConfig(AppConfig):
    name = 'geeksurvey'

    def ready(self):
        import geeksurvey.signals
        import payments.signals

