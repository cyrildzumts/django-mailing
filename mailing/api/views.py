from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.core.exceptions import PermissionDenied, SuspiciousOperation, ObjectDoesNotExist
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from mailing import constants as MAILING_CONSTANTS
from mailing.models import MailCampaign
from mailing import mailing_service
import logging
import uuid
logger = logging.getLogger(__name__)


@api_view(['POST'])
def create_campaign(request):
    username = request.user.username
    if not request.user.has_perm('mailing.can_send_mailcampaign'):
        logger.warning("Mailing : PermissionDenied to user %s for path %s", username, request.path)
        return Response(data={'success': False}, status=status.HTTP_401_UNAUTHORIZED)
    
    logger.info(f"API: create mail campaign request from user {username}")
    if request.method != 'POST':
        return Response({'status': False, 'errror': 'Bad request. Use POST instead'}, status=status.HTTP_400_BAD_REQUEST)
    
    data = mailing_service.create_campaign(request.POST.copy(), request.FILES)
    
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def update_campaign(request, campaign_uuid):
    username = request.user.username
    if not request.user.has_perm('mailing.can_send_mailcampaign'):
        logger.warning("Mailing : PermissionDenied to user %s for path %s", username, request.path)
        return Response(data={'success': False}, status=status.HTTP_401_UNAUTHORIZED)
    
    logger.info(f"API: update mail campaign request from user {username}")
    if request.method != 'POST':
        return Response({'status': False, 'errror': 'Bad request. Use POST instead'}, status=status.HTTP_400_BAD_REQUEST)
    
    data = mailing_service.update_campaign(campaign_uuid, request.POST.copy(), request.FILES)
    
    return Response(data=data, status=status.HTTP_200_OK)



@api_view(['POST'])
def campaign_generate_mail(request, campaign_uuid=None):
    username = request.user.username
    if not request.user.has_perm('mailing.can_send_mailcampaign'):
        logger.warning("Mailing : PermissionDenied to user %s for path %s", username, request.path)
        return Response(data={'success': False}, status=status.HTTP_401_UNAUTHORIZED)

    logger.info(f"API: send mail campaign request from user {username}")
    try:
        campaign = MailCampaign.objects.get(campaign_uuid=campaign_uuid)
        mailing_service.generate_mail_campaign(campaign, request)
        return Response(data={'success': True})
    except ObjectDoesNotExist as e:
        return Response(data={'success': False}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e :
        
        logger.warning(f"Mailing : MailCampaign HTML not generate : {e}")
        return Response(data={'success': False}, status=status.HTTP_400_BAD_REQUEST)
    