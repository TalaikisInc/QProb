

from django.apps import AppConfig


class AggregatorConfig(AppConfig):
    name = 'aggregator'

    def ready(self):
        import aggregator.signals
