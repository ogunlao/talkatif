from django.apps import AppConfig


class DebateConfig(AppConfig):
    name = 'debate'

    def ready(self):
        import debate.signals
