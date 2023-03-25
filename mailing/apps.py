from django.apps import AppConfig
from django.conf import settings
from mailing import constants
import django
import logging

logger = logging.getLogger(__name__)

class MailingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mailing'
    
    def ready(self):
        logger.info("Django-amiling starting. Checking required settings ...")
        missing_settings = []
        for setting in constants.REQUIRED_SETTINGS:
            if not hasattr(settings, setting):
                missing_settings.append(setting)
        if len(missing_settings) > 0:
            msg = f"Django-mailing can not start. Required settings are missing : {missing_settings}. Please provide the settings in the global settings"
            logger.error(msg)
            raise Exception(msg)
        
        import mailing.signals
        logger.info(f"Django-Mailing Started. Django Version {django.get_version()}")
