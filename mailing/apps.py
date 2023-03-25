from django.apps import AppConfig
import django
import logging

logger = logging.getLogger(__name__)

class MailingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mailing'
    
    def ready(self):
        import mailing.signals
        logger.info(f"Django-Mailing Started. Django Version {django.get_version()}")
