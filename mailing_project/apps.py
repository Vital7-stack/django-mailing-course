from django.apps import AppConfig

class MailingProjectConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mailing_project'

    def ready(self):
        import mailing_project.admin