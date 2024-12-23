from django.apps import AppConfig


class WarehousesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'warehouses'
    verbose_name = 'Складское'

    def ready(self):
        import warehouses.signals
