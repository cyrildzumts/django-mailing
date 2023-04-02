import importlib
from django.core.mail import send_mail, send_mass_mail, EmailMessage
from django.http import HttpRequest
from django.utils import timezone
from django.db.models import Q,F
from django.contrib.auth.models import User
from celery import shared_task
from django.template.loader import render_to_string
from django.dispatch import receiver
from django.conf import settings
from mailing import constants as MAILING_CONSTANTS
import logging
import copy

from mailing.models import MailCampaign

logger = logging.getLogger(__name__)


def splitify(a, n):
    k, m = divmod(len(a), n)
    return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))


def build_required_context(request):
    MAILING_TEMPLATE_PROCESSORS = getattr(settings, MAILING_CONSTANTS.SETTINGS_MAILING_TEMPLATE_CONTEXTS)
    template_context = {}
    processors = []
    for e in MAILING_TEMPLATE_PROCESSORS:
        module = importlib.import_module(e.get('module'))
        if hasattr(module, e.get('processor')):
            processor = getattr(module, e.get('processor'))
            template_context.update(processor(request))
            processors.append(processor)
        else:
            msg = f"Error while looking up for template processors defined by {e}"
            logger.warn(msg)
            raise Exception(msg)
    
    return template_context

def generate_mail_campaign(campaign, template_context):
    logger.info("generate_mail_campaign")
    context = copy.deepcopy(template_context)
    context.update({'campaign': campaign, 'MAIL_TITLE': campaign.name})
    if campaign.campaign_type == MAILING_CONSTANTS.MAIL_CAMPAIGN_STANDARD:
        generate_standard_campaign(campaign, context)
        
    elif campaign.campaign_type == MAILING_CONSTANTS.MAIL_CAMPAIGN_MULTIPLE_PRODUCT:
        generate_product_campaign(campaign, context)
        
        

def generate_standard_campaign(campaign, template_context):
    logger.info("generate_standard_campaign")
    CAMPAIGN_MAPPING = getattr(settings, MAILING_CONSTANTS.SETTINGS_MAIL_CAMPAIGN_MAPPING)
    mapping = CAMPAIGN_MAPPING[str(campaign.campaign_type)]
    template_name = mapping['template']
    mail_html = render_to_string(template_name, template_context)
    if mail_html:
        with open(f"{campaign.slug}.html", 'w') as f:
            f.write(mail_html)
            logger.info(f" Mail Campaign {campaign.name} html file created")
        
        email_context = {
            'mail': mail_html,
            'subject': campaign.name
        }
        send_mail_campaign_task.apply_async(args=[email_context])
        
        

def generate_product_campaign(campaign, template_context):
    logger.info("generate_product_campaign")
    CAMPAIGN_MAPPING = getattr(settings, MAILING_CONSTANTS.SETTINGS_MAIL_CAMPAIGN_MAPPING)
    mapping = CAMPAIGN_MAPPING[str(campaign.campaign_type)]
    template_name = mapping['template']
    mod_import = mapping['import']
    mod_method = mapping['method']
    context_name = mapping['context_name']
    module = importlib.import_module(mapping['import'])
    mail_html = None
    if hasattr(module, mod_method):
        callable = getattr(module, mod_method)
        list_entries = callable()
        context_var = list(splitify(list_entries, 4))
        template_context[context_name] = context_var
        mail_html = render_to_string(template_name, template_context)
    if mail_html:
        with open(f"{campaign.slug}.html", 'w') as f:
            f.write(mail_html)
            logger.info(f" Mail Campaign {campaign.name} html file created")
        
        email_context = {
            'mail': mail_html,
            'subject': campaign.name
        }
        send_mail_campaign_task.apply_async(args=[email_context])

def send_campaign_mail(campaign, template_context, template_name):
    context = copy.deepcopy(template_context)
    context.update({'campaign': campaign, 'MAIL_TITLE': campaign.name})
    mail_html = render_to_string(template_name, context)
    email_context = {
        'mail': mail_html,
        'subject': campaign.name
    }
    send_mail_campaign_task.apply_async(args=[email_context])

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
    

@shared_task
def publish_scheduled_mail_campaigns():
    
    NOW = timezone.datetime.now()
    logger.info(f"Running publish_scheduled_mail_campaigns - current time : {NOW}")
    #Published Scheduled Product
    SCHEDULED_FILTER = Q(scheduled_at__lte=NOW) & Q(published_status=MAILING_CONSTANTS.PUBLISHED_STATUS_SCHEDULED)
    queryset = MailCampaign.objects.filter(SCHEDULED_FILTER)
    if not queryset.exists():
        return
    
    sent_campaign_ids = []
    try:
        request = HttpRequest()
        template_context = build_required_context(request)
        #template_name = getattr(settings, MAILING_CONSTANTS.SETTINGS_DEFAULT_MAIL_TEMPLATE)
        sent_campaign_ids = []
        for campaign in queryset:
            generate_mail_campaign(campaign, template_context)
            sent_campaign_ids.append(campaign.pk)
            
        
    except Exception as e:
        logger.warn(f"publish_scheduled_mail_campaigns : An exception occured while publishing Campaigns. Published campaigns : {sent_campaign_ids} - Exception {e}", e)
        
        
    if len(sent_campaign_ids):
        a = queryset.filter(id__in=sent_campaign_ids).update(published_status=MAILING_CONSTANTS.PUBLISHED_STATUS_PUBLISHED, published_at=NOW)
        logger.info(f"MailCampaign SCHEDULED TASK: Published {a} scheduled campaigns")
    