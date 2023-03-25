from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from mailing.resources import ui_strings as UI_STRINGS
import uuid


# Create your models here.

def upload_campaign_to(instance, filename):
    return f"mailing/{instance.key}/{filename}"


class MailCampaign(models.Model):
    key = models.CharField(max_length=64)
    name = models.CharField(max_length=128)
    headerText = models.CharField(max_length=300)
    bodyText = models.CharField(max_length=300)
    cta = models.CharField(max_length=128)
    target_link = models.CharField(max_length=300)
    description = models.CharField(max_length=300, blank=True, null=True)
    added_by = models.ForeignKey(User, related_name='mail_campaigns', blank=True, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False, editable=False)
    last_changed_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to=upload_campaign_to, blank=True, null=True)
    slug = models.SlugField(max_length=250, blank=True, null=True)
    view_count = models.IntegerField(blank=True, null=True, default=0)
    campaign_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    FORM_FIELDS = ['name','key', 'headerText','bodyText','cta','target_link', 'description', 'image', 'added_by', ]

    DATATABLE_ACTIONS = ['open','update','delete']
    
    class Meta:
        ordering = ['name','-last_changed_at','-created_at']
        permissions = [
            ('can_send_mailcampaign', UI_STRINGS.UI_PERMISSION_CAN_SEND_MAIL),
        ]
    def __str__(self) -> str:
        return self.name

    def get_image_url(self):
        if self.image:
            return self.image.url
        return None
    
    @property
    def campaign_link(self):
        return f"{self.target_link}?campaign={self.key}&source=email"
    

    def get_absolute_url(self):
        return reverse("mailing:mail-campaign", kwargs={"slug": self.slug, "campaign_uuid": self.campaign_uuid})
    
    
    def get_slug_url(self):
        return reverse("mailing:mail-campaign", kwargs={"slug": self.slug, "campaign_uuid": self.campaign_uuid})
    
    def get_dashboard_url(self):
        return reverse("mailing:campaign-detail", kwargs={"campaign_uuid": self.campaign_uuid})
    
    def get_update_url(self):
        return reverse("mailing:campaign-update", kwargs={"slug": self.slug, "campaign_uuid": self.campaign_uuid})