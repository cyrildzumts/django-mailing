
from django.template.loader import render_to_string, get_template
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F
from django.conf import settings
from mailing.models import MailCampaign
from mailing import constants as MAILING_CONSTANTS, tasks

import importlib
import logging

logger = logging.getLogger(__name__)

def splitify(a, n):
    k, m = divmod(len(a), n)
    return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))

def populate_with_required_context(request, context):
    MAILING_TEMPLATE_PROCESSORS = getattr(settings, MAILING_CONSTANTS.SETTINGS_MAILING_TEMPLATE_CONTEXTS)
    template_context = {}
    template_context.update(context)
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




def generate_mail_campaign_template(campaign, request):
    logger.info("generate_mail_campaign")
    try:
        if campaign.campaign_type == MAILING_CONSTANTS.MAIL_CAMPAIGN_STANDARD:
            return generate_standard_campaign_template(campaign, request)
            
        elif campaign.campaign_type == MAILING_CONSTANTS.MAIL_CAMPAIGN_MULTIPLE_PRODUCT:
            return generate_product_campaign_template(campaign, request)
    
    except Exception as e:
        logger.error(f"Error on generation mail campaign for campaign {campaign}. Error : {e}")
        raise e
             

def generate_standard_campaign_template(campaign, request):
    logger.info("generate_standard_campaign")
    CAMPAIGN_MAPPING = getattr(settings, MAILING_CONSTANTS.SETTINGS_MAIL_CAMPAIGN_MAPPING)
    mapping = CAMPAIGN_MAPPING[str(campaign.campaign_type)]
    template_name = mapping['template']
    context = populate_with_required_context(request,{'campaign': campaign, 'MAIL_TITLE': campaign.name})
    mail_html = render_to_string(template_name, context)
    return {'mail': mail_html,'subject': campaign.name }
    
        
        

def generate_product_campaign_template(campaign, request):
    logger.info("generate_product_campaign")
    CAMPAIGN_MAPPING = getattr(settings, MAILING_CONSTANTS.SETTINGS_MAIL_CAMPAIGN_MAPPING)
    mapping = CAMPAIGN_MAPPING[str(campaign.campaign_type)]
    logger.info(f"mapping : {mapping}")
    template_name = mapping['template']
    mod_import = mapping['import']
    mod_method = mapping['method']
    argument = mapping['argument']
    context_name = mapping['context_name']
    
    context = populate_with_required_context(request,{'campaign': campaign, 'MAIL_TITLE': campaign.name})
    module = importlib.import_module(mod_import)
    mail_html = None
    
    if hasattr(module, mod_method):
        callable = getattr(module, mod_method)
        if argument:
            arg = getattr(campaign, argument)
            if arg is None or arg == "":
                logger.warn(f"campaign {campaign} arg is empty : {arg}. Campaign not generated.")
                raise Exception(f"Campagin Mail not sent. setting \"argument\" is missing or invalid")
            list_entries = callable(arg)
        else:
            list_entries = callable()
        if list_entries:
            context_var = list(splitify(list_entries, 4))
        else:
            context_var = None
            logger.warning(f"No context var found  for campaign {campaign}. List entries is empty")
            raise Exception(f"Campagin Mail not sent. No Context products is empty.")
        context[context_name] = context_var
        logger.info(f"generating Campaign Mail following context : context : {context_name} - context content : {context_var}")
        mail_html = render_to_string(template_name, context)
    return {'mail': mail_html,'subject': campaign.name }