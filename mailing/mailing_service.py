from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from mailing.models import MailCampaign
from mailing.forms import MailCampaignForm
from mailing import constants as MAILING_CONSTANTS
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
    

def generate_mail_campaign_html(campaign):
    template_name = getattr(settings, MAILING_CONSTANTS.SETTINGS_DEFAULT_MAIL_TEMPLATE)
    mail_html = render_to_string(template_name, {'campaign': campaign})
    with open(f"{campaign.slug}.html", 'w') as f:
        f.write(mail_html)
        logger.info(f" Mail Campaign {campaign.name} html file created")
        
def send_mail_campaign(campaign):
    template_name = getattr(settings, MAILING_CONSTANTS.SETTINGS_DEFAULT_MAIL_TEMPLATE)
    mail_html = render_to_string(template_name, {'campaign': campaign})
    
    
    



