from users.api.views import ProfileView, UserView, EmailCheckView, UserCheckView, CreateUserView
from django.urls import path, include

app_name='users-api'

urlpatterns = [
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
    path('details/<str:pk>/', UserView.as_view(), name="usuario"),
    path('profile/<str:pk>/', ProfileView.as_view(), name="profile"),
    path('user/<user>/', UserCheckView.as_view(), name="user_check"),
    path('email/<email>/', EmailCheckView.as_view(), name="email_check"),
    path('newuser/', CreateUserView.as_view(), name="new_user"),
]