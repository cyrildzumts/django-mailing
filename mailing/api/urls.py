from django.urls import path
from mailing.api import views

app_name = 'mailing-api'

urlpatterns = [
     path('create-mail-campaign/', views.create_campaign, name='api-create-campaign'),
     path('update-mail-campaign/<uuid:campaign_uuid>/', views.update_campaign, name='api-update-campaign'),
]