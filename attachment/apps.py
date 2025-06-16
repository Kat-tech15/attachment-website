from django.apps import AppConfig



class AttachmentAppConfig(AppConfig):
    name = 'attachment'
    verbose_name = 'Attachment Management'

    def ready(self):
        # Import signals to ensure they are registered
        import attachment.signals