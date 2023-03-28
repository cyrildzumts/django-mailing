from django.core.mail import send_mail, send_mass_mail, EmailMessage
from django.utils import timezone
from django.db.models import Q,F
from django.contrib.auth.models import User
from celery import shared_task
from django.template.loader import render_to_string
from django.dispatch import receiver
from django.conf import settings
from mailing import constants as MAILING_CONSTANTS
import logging

from mailing.models import MailCampaign

logger = logging.getLogger(__name__)

#@shared_task
def send_mail_task(email_context=None):
    if email_context is not None and isinstance(email_context, dict):
        try:
            if email_context.get('use_template') or email_context.get('use_template') is None:
                template_name = email_context['template_name']
                context = email_context['context']
                html_message = render_to_string(template_name, context)
                send_mail(
                    email_context['title'],
                    None,
                    settings.DEFAULT_FROM_EMAIL,
                    [email_context['recipient_email']],
                    html_message=html_message
                )
            else:
                send_mail(
                    email_context['title'],
                    None,
                    settings.DEFAULT_FROM_EMAIL,
                    [email_context['recipient_email']],
                    html_message=email_context['message']
                )
        except KeyError as e:
            logger.error(f"send_mail_task : template_name not available. Mail not send. email_context : {email_context}")
            return
        
    else:
        logger.warn(f"send_mail_task: email_context missing or is not a dict. email_context : {email_context}")
        
@shared_task
def send_mail_campaign_task(email_context=None):
    if email_context is not None and isinstance(email_context, dict):
        try:
            bcc_list = []
            user_list = User.objects.filter(account__email_validated=True, account__account_type=MAILING_CONSTANTS.ACCOUNT_PRIVATE)
            if not user_list.exists():
                logger.warning(f"Mail Campaign Task : no matching users found. No mails sent")
                return
            bcc_list = list(user_list.values_list('email', flat=True))
            email_message = EmailMessage(email_context['subject'], body=email_context['mail'],from_email=settings.DEFAULT_FROM_EMAIL,bcc=bcc_list)
            email_message.content_subtype = MAILING_CONSTANTS.EMAIL_MESSAGE_CONTENT_TYPE
            email_message.send()
            # send_mail(
            #     email_context['title'],
            #     None,
            #     settings.DEFAULT_FROM_EMAIL,
            #     [email_context['recipient_email']],
            #     html_message=email_context['message']
            # )
        except KeyError as e:
            logger.error(f"send_mail_task : template_name not available. Mail not send. email_context : {email_context}")
            return
        
    else:
        logger.warn(f"send_mail_task: email_context missing or is not a dict. email_context : {email_context}")
        
        

#@shared_task
def send_mass_mail_task(email_context=None):
    
    # TODO : make sending email based on Django Template System.
    if email_context is not None:

        try:
            template_name = email_context['template_name']
        except KeyError as e:
            logger.debug("template_name not available")
        #message = loader.render_to_string(template_name, {'email': email_context})

        html_message = render_to_string(template_name, email_context['context'])
        messages = ()
        send_mail(
            email_context['title'],
            None,
            settings.DEFAULT_FROM_EMAIL,
            [email_context['recipient_email']],
            html_message=html_message
        )
    else:
        logger.warn("send_mass_mail_task: email_context or recipients not available")
        

@shared_task
def campaign_track_visit(param_dicts):
    logger.info(f"Updating MailCampaign Views count : {param_dicts}")
    qs = MailCampaign.objects.filter(key=param_dicts[MAILING_CONSTANTS.PARAM_CAMPAIGN_KEY])
    if not qs.exists():
        return
    qs.update(view_count=F('view_count') + 1)