from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('create_dispositor/', views.create_dispositor, name='create_dispositor'),
    path('create_paramedic/', views.create_paramedic, name='create_paramedic'),
    path('paramedic_settings/', views.paramedic_settings, name='paramedic_settings'),
    path('settings', views.settings, name='settings'),
    path('create_emergency_alert_api/', views.create_emergency_alert_api, name='create_emergency_alert_api')
]
