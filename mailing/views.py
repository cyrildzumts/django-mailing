from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import PermissionDenied, SuspiciousOperation, ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User, Group, Permission
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from mailing.models import MailCampaign
from mailing.forms import MailCampaignForm
from mailing import constants as MAILING_CONSTANTS
from mailing import mailing_service
from mailing.resources import ui_strings as UI_STRINGS
import csv
import logging

logger = logging.getLogger(__name__)
# Create your views here.


@login_required
def campaigns(request):
    username = request.user.username
    if not request.user.has_perm('mailing.view_mailcampaign'):
        logger.warning("Mailing : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    template_name = getattr(settings, MAILING_CONSTANTS.SETTINGS_TEMPLATE_CAMPAIGNS_PAGE, MAILING_CONSTANTS.DEFAULT_MAILING_CAMPAIGNS_PAGE)
    page_title = UI_STRINGS.UI_MAIL_CAMPAIGN_LIST_PAGE_TITLE
    context = {}

    queryset = MailCampaign.objects.all()

    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, MAILING_CONSTANTS.PAGINATED_BY)
    try:
        list_set = paginator.page(page)
    except PageNotAnInteger:
        list_set = paginator.page(1)
    except EmptyPage:
        list_set = None
    context['page_title'] = page_title
    context['campaign_list'] = list_set
    context['content_title'] = page_title
    context['BASE_TEMPLATE'] = getattr(settings, MAILING_CONSTANTS.SETTINGS_BASE_TEMPLATE_INHERIT)
    return render(request,template_name, context)


@login_required
def campaign_create(request):
    template_name = getattr(settings, MAILING_CONSTANTS.SETTINGS_TEMPLATE_CAMPAIGN_CREATE_PAGE, MAILING_CONSTANTS.DEFAULT_MAILING_CAMPAIGN_CREATE_PAGE)
    page_title = UI_STRINGS.UI_MAIL_CAMPAIGN_CREATE_PAGE_TITLE
    username = request.user.username
    if not request.user.has_perm('mailing.add_mailcampaign'):
        logger.warning("Mailing : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied
    context = {
        'page_title': page_title,
    }
    form = None
    
    username = request.user.username
    if request.method == 'POST':
        data = mailing_service.create_campaign(request.POST.copy(), request.FILES)
        if data['success']:
            messages.success(request, data.get('message'))
            logger.info(f'Mail Campaign {data.get("name")} created by user \"{username}\"')
            return redirect(data.get('url'))
        else:
            messages.error(request, data.get('message'))
            messages.error(request, data.get('errors'))
            logger.error(f'Error on creating new  mail campaign. Action requested by user \"{username}\"')
            logger.error(data.get('errors'))
    else:
        form = MailCampaignForm()
    context['form'] = form
    context['DESCRIPTION_MAX_SIZE'] = MAILING_CONSTANTS.DESCRIPTION_MAX_SIZE
    context['content_title'] = page_title
    context['BASE_TEMPLATE'] = getattr(settings, MAILING_CONSTANTS.SETTINGS_BASE_TEMPLATE_INHERIT)
    return render(request, template_name, context)


@login_required
def campaign_detail(request,slug, campaign_uuid=None):
    username = request.user.username
    if not request.user.has_perm('mailing.view_mailcampaign'):
        logger.warning("Mailing : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    template_name = getattr(settings, MAILING_CONSTANTS.SETTINGS_TEMPLATE_CAMPAIGN_PAGE, MAILING_CONSTANTS.DEFAULT_MAILING_CAMPAIGN_PAGE)
    page_title = UI_STRINGS.UI_MAIL_CAMPAIGN_PAGE_TITLE
    

    campaign = get_object_or_404(MailCampaign, slug=slug, campaign_uuid=campaign_uuid)
    context = {
        'page_title': page_title,
        'campaign': campaign,
        'content_title': page_title
    }
    context['BASE_TEMPLATE'] = getattr(settings,MAILING_CONSTANTS.SETTINGS_BASE_TEMPLATE_INHERIT)
    return render(request,template_name, context)


@login_required
def campaign_update(request, slug, campaign_uuid):
    username = request.user.username
    if not request.user.has_perm('mailing.change_mailcampaign'):
        logger.warning("Mailing : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied


    template_name = getattr(settings, MAILING_CONSTANTS.SETTINGS_TEMPLATE_CAMPAIGN_UPDATE_PAGE, MAILING_CONSTANTS.DEFAULT_MAILING_CAMPAIGN_UPDATE_PAGE)
    page_title = UI_STRINGS.UI_MAIL_CAMPAIGN_UPDATE_PAGE_TITLE
    context = {
        'page_title': page_title,
    }
    form = None
    campaign = get_object_or_404(MailCampaign, slug=slug,campaign_uuid=campaign_uuid)
    if request.method == 'POST':
        data = mailing_service.update_campaign(campaign_uuid, request.POST.copy(), request.FILES)
        if data.get('success'):
            messages.success(request, data.get('message'))
            logger.info(f'mail campaign {campaign.name} updated by user \"{username}\"')
            return redirect(data.get('url'))
        else:
            messages.error(request, data.get('message'))
            logger.error(f'Error on updating mail campaign. Action requested by user \"{username}\"')
            logger.error(data.get('errors'))
    else:
        form = MailCampaignForm(instance=campaign)
    context['form'] = form
    context['campaign'] = campaign
    context['DESCRIPTION_MAX_SIZE'] = MAILING_CONSTANTS.DESCRIPTION_MAX_SIZE
    context['BASE_TEMPLATE'] = getattr(settings, MAILING_CONSTANTS.SETTINGS_BASE_TEMPLATE_INHERIT)
    return render(request, template_name, context)

@login_required
def campaign_delete(request, campaign_uuid=None):
    username = request.user.username
    if not request.user.has_perm('mailing.delete_mailcampaign'):
        logger.warning("Mailing : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied


    if request.method != "POST":
        raise SuspiciousOperation('Bad request')

    campaign = get_object_or_404(MailCampaign, campaign_uuid=campaign_uuid)
    MailCampaign.objects.filter(pk=campaign.pk).delete()
    logger.info(f'MailCampaign \"{campaign.name}\" deleted by user \"{request.user.username}\"')
    messages.success(request, _('Mail Campaign deleted'))
    return redirect('mailing:mail-campaigns')

@login_required
def campaigns_delete(request):
    username = request.user.username
    if not request.user.has_perm('mailing.delete_mailcampaign'):
        logger.warning("Mailing : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied


    if request.method != "POST":
        raise SuspiciousOperation('Bad request')

    id_list = request.POST.copy().getlist('campaigns')

    if len(id_list):
        campaign_list = list(map(int, id_list))
        MailCampaign.objects.filter(id__in=campaign_list).delete()
        messages.success(request, f"MailCampaigns \"{id_list}\" deleted")
        logger.info(f"MailCampaigns \"{id_list}\" deleted by user {username}")
        
    else:
        messages.error(request, f"MailCampaign \"{id_list}\" could not be deleted")
        logger.error(f"ID list invalid. Error : {id_list}")
    return redirect('mailing:mail-campaigns')

@login_required
def campaign_generate_mail(request, campaign_uuid=None):
    username = request.user.username
    if not request.user.has_perm('mailing.can_send_mailcampaign'):
        logger.warning("Mailing : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    campaign = get_object_or_404(MailCampaign,campaign_uuid=campaign_uuid)
    
    try:
        mailing_service.generate_mail_campaign_html(campaign)
        messages.success(request, _('MailCampaign HTML not generated'))
    except Exception as e :
        messages.warning(request, _('MailCampaign HTML not generated'))
        logger.warning(f"Mailing : MailCampaign HTML not generate : {e}")
    
    return redirect('mailing:campaign-detail', campaign_uuid=campaign_uuid)


@login_required
def campaign_generate_html(request, campaign_uuid=None):
    username = request.user.username
    if not request.user.has_perm('mailing.can_send_mailcampaign'):
        logger.warning("Mailing : PermissionDenied to user %s for path %s", username, request.path)
        raise PermissionDenied

    campaign = get_object_or_404(MailCampaign,campaign_uuid=campaign_uuid)
    
    try:
        mailing_service.generate_mail_campaign_html(campaign)
        messages.success(request, _('MailCampaign HTML not generated'))
    except Exception as e :
        messages.warning(request, _('MailCampaign HTML not generated'))
        logger.warning(f"Mailing : MailCampaign HTML not generate : {e}")
    
    return redirect('mailing:campaign-detail', campaign_uuid=campaign_uuid)


