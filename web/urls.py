from django.urls import path
from .views import index, ts, ftp, jc, emby, axie

app_name='web'

urlpatterns = [
    path('', index, name='index'),
    path('ts/', ts, name="ts"),
    path('ftp/', ftp, name="ftp"),
    path('jc/', jc, name="jc"),
    path('emby/', emby, name="emby"),
    path('axie/', axie, name="axie"),
]