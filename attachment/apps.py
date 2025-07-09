from django.apps import AppConfig



class AttachmentAppConfig(AppConfig):
    name = 'attachment'
    verbose_name = 'Attachment Management'

        # Import signals to ensure they are registered
    def ready(self):
       pass