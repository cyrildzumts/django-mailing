from mailing.models import MailCampaign
from django import forms
from django.core.exceptions import ObjectDoesNotExist, ValidationError


class MailCampaignForm(forms.ModelForm):

    class Meta:
        model = MailCampaign
        fields = MailCampaign.FORM_FIELDS

    def clean_name(self):
        name = self.cleaned_data.get('name')
        try:
           instance = MailCampaign.objects.get(name__iexact=name)
        except ObjectDoesNotExist:
            pass
        else:
            if self.instance != instance:
                raise ValidationError(message=f"A mail campaign with the name \"{name}\" already exists")
            
        return name
    
    def clean_key(self):
        key = self.cleaned_data.get('key')
        try:
           instance = MailCampaign.objects.get(key__iexact=key)
        except ObjectDoesNotExist:
            pass
        else:
            if self.instance != instance:
                raise ValidationError(message=f"A mail campaign with the title \"{key}\" already exists")
            
        return key
