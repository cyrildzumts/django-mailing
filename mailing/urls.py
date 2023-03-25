from django.urls import path
from mailing import views

app_name = 'mailing'

urlpatterns = [
    path('', views.campaigns, name='campaigns'),
    path('campaigns/', views.campaigns, name='campaigns'),
    path('campaigns/create/', views.campaign_create, name='campaign-create'),
    path('campaigns/delete/', views.campaigns_delete, name='campaigns-delete'),
    path('campaigns/delete/<uuid:campaign_uuid>/', views.campaign_delete, name='campaign-delete'),
    path('campaigns/detail/generate-html/<uuid:campaign_uuid>/', views.campaign_generate_html, name='generate-html'),
    path('campaigns/detail/generate-mail/<uuid:campaign_uuid>/', views.campaign_generate_mail, name='generate-mail'),
    path('campaigns/detail/<slug:slug>/<uuid:campaign_uuid>/', views.campaign_detail, name='campaign-detail'),
    path('campaigns/update/<slug:slug>/<uuid:campaign_uuid>/', views.campaign_update, name='campaign-update'),
]
