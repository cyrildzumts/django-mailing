from django.template import RequestContext, Template
from django.db import models
from django.apps import apps
from django.template.loader import render_to_string, get_template
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F
from django.conf import settings
from mailing.models import MailCampaign
from mailing.forms import MailCampaignForm
from mailing import mailing_tools
from mailing import constants as MAILING_CONSTANTS, tasks

import importlib
import datetime
import logging
import os
import csv

logger = logging.getLogger(__name__)


def splitify(a, n):
    k, m = divmod(len(a), n)
    return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))



def create_campaign(postdata, files):
    form = MailCampaignForm(postdata, files=files)
    if form.is_valid():
        campaign = form.save()
        return {'success': True, 'name': campaign.name, 'message': _('New MailCampaign created'),'url_text': 'Open  Campaign', 'url': campaign.get_dashboard_url()}
    else:
        
        logger.error(form.errors.items())
        return {'success': False, 'message': _('MailCampaign not created'), 'errors': form.errors}


def update_campaign(campaign_uuid, postdata, files):
    try:
        campaign = MailCampaign.objects.get(campaign_uuid=campaign_uuid)
        form = MailCampaignForm(postdata, files=files, instance=campaign)
        if form.is_valid():
            campaign = form.save()
            return {'success': True,'name': campaign.name, 'message': _('MailCampaign updated'),'url_text': 'Open  Campaign', 'url': campaign.get_dashboard_url()}
        else:
            
            logger.error(form.errors.items())
            return {'success': False, 'message': _('MailCampaign not updated'), 'errors': form.errors}
    except ObjectDoesNotExist as e:
        return {'success': False, 'message': _('MailCampaign not found'), 'errors': str(e)}


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




def generate_mail_campaign(campaign, request, send_mail=False):
    logger.info("generate_mail_campaign")
    try:
        mail_context = mailing_tools.generate_mail_campaign_template(campaign, request)
        mail_html = mail_context['mail_html']
        if mail_html:
            with open(f"{MAILING_CONSTANTS.MAILING_DIR}/{campaign.key}/{campaign.key}.html", 'w') as f:
                f.write(mail_html)
                logger.info(f" Mail Campaign {campaign.name} html file created")
            if send_mail:
                tasks.send_mail_campaign_task.apply_async(args=[mail_context])
    
    except Exception as e:
        logger.error(f"Error on generation mail campaign for campaign {campaign}. Error : {e}")
        raise e
             

def generate_standard_campaign(campaign, request, send_mail=False):
    logger.info("generate_standard_campaign")
    CAMPAIGN_MAPPING = getattr(settings, MAILING_CONSTANTS.SETTINGS_MAIL_CAMPAIGN_MAPPING)
    mapping = CAMPAIGN_MAPPING[str(campaign.campaign_type)]
    template_name = mapping['template']
    context = populate_with_required_context(request,{'campaign': campaign, 'MAIL_TITLE': campaign.name})
    mail_html = render_to_string(template_name, context)
    if mail_html:
        with open(f"{campaign.slug}.html", 'w') as f:
            f.write(mail_html)
            logger.info(f" Mail Campaign {campaign.name} html file created")
        
        if send_mail:
            tasks.send_mail_campaign_task.apply_async(args=[{'mail': mail_html,'subject': campaign.name }])
        
        

def generate_product_campaign(campaign, request, send_mail=False):
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
    if mail_html:
        with open(f"{campaign.slug}.html", 'w') as f:
            f.write(mail_html)
            logger.info(f" Mail Campaign {campaign.name} html file created")
        
        if send_mail:
            tasks.send_mail_campaign_task.apply_async(args=[{'mail': mail_html,'subject': campaign.name }])
        



def generate_mail_campaign_html(campaign, request):
    logger.info("generate_mail_campaign html")
    try:
        if campaign.campaign_type == MAILING_CONSTANTS.MAIL_CAMPAIGN_STANDARD:
            generate_standard_campaign(campaign, request, False)
            
        elif campaign.campaign_type == MAILING_CONSTANTS.MAIL_CAMPAIGN_MULTIPLE_PRODUCT:
            generate_product_campaign(campaign, request, False)
    
    except Exception as e:
        logger.error(f"Error on generation of html for mail campaign {campaign}. Error : {e}")
        raise e
        
        
def send_mail_campaign(campaign, request):
    template_name = getattr(settings, MAILING_CONSTANTS.SETTINGS_DEFAULT_MAIL_TEMPLATE)
    context = populate_with_required_context(request,{'campaign': campaign, 'MAIL_TITLE': campaign.name})
    mail_html = render_to_string(template_name, context)
    email_context = {
        'mail': mail_html,
        'subject': campaign.name
    }
    tasks.send_mail_campaign_task.apply_async(args=[email_context])
    
    
def campaign_new_visit(param_dicts):
    tasks.campaign_track_visit.apply_async(args=[param_dicts])
    
    
    
    



