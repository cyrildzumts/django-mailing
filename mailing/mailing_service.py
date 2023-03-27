from django.template import RequestContext, Template
from django.template.loader import render_to_string, get_template
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from mailing.models import MailCampaign
from mailing.forms import MailCampaignForm
from mailing import constants as MAILING_CONSTANTS
import importlib
import datetime
import logging
import os
import csv

logger = logging.getLogger(__name__)




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
    MAILING_TEMPLATE_CONTEXTS_KEYS = getattr(settings, MAILING_CONSTANTS.SETTINGS_MAILING_TEMPLATE_CONTEXTS_KEYS)
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
    requestContext = RequestContext(request, context, processors=processors)
    logger.info(f"Populating context with {MAILING_TEMPLATE_PROCESSORS} - RequestContext : {requestContext} - PROCESSORS : {processors} -Context : {template_context}")
    
    return requestContext

def generate_mail_campaign_html(campaign, request):
    template_name = getattr(settings, MAILING_CONSTANTS.SETTINGS_DEFAULT_MAIL_TEMPLATE)
    context = populate_with_required_context(request,{'campaign': campaign})
    mail_html = render_to_string(template_name, context)
    with open(f"{campaign.slug}.html", 'w') as f:
        f.write(mail_html)
        logger.info(f" Mail Campaign {campaign.name} html file created")
        
        
def send_mail_campaign(campaign, context):
    template_name = getattr(settings, MAILING_CONSTANTS.SETTINGS_DEFAULT_MAIL_TEMPLATE)
    mail_html = render_to_string(template_name, context)
    
    
    



