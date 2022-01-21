from .views import ContactView, AllUsersView
from django.urls import path

app_name='chat-api'


urlpatterns = [
    path('contactos/<str:pk>/', ContactView.as_view(), name='contactos'),
    path('new_chat/<str:user>/<str:contact>/', AllUsersView.as_view(), name='contactos'),
]