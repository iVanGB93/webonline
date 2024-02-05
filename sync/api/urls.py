from sync.api.views import StatusCheckView
from django.urls import path

app_name='sync-api'

urlpatterns = [
    path('status/<str:name>/', StatusCheckView.as_view(), name="status"),
]