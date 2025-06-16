from django.apps import AppConfig


class AttachmentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'attachment'

class AttachmentAppConfig(AppConfig):
    name = 'attachment'
    verbose_name = 'Attachment Management'

    def ready(self):
        # Import signals to ensure they are registered
        import attachment.signals