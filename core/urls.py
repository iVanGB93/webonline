from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views



urlpatterns = [
    path('administrador/', admin.site.urls),
    path('', include('web.urls')),
    path('sync/', include('sync.urls')),
    path('sorteo/', include('sorteo.urls')),
    path('cotilleo/', include('forum.urls')),
    path('portal/', include('portal.urls')),
    path('api/servicios/', include('servicios.api.urls')),
    path('users/', include('users.urls')),
    path('api/users/', include('users.api.urls')),
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name="users/password_reset.html"), name="reset_password"),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="users/password_reset_send.html"), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="users/password_reset_form.html"), name="password_reset_confirm"),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="users/password_reset_done.html"), name="password_reset_complete"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)