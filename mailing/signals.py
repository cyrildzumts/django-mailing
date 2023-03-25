from django.dispatch import receiver
from django.utils.text import slugify
from django.db.models.signals import post_save, pre_save
import logging

from mailing.models import MailCampaign


logger = logging.getLogger(__name__)

@receiver(pre_save, sender=MailCampaign)
def generate_campaign_slug(sender, instance, *args, **kwargs):
    instance.slug = slugify(f"{instance.name}-{instance.key}")