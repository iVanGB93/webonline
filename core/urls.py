from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView


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
    path('portal/password-reset/confirm/<uidb64>/<token>/',
        TemplateView.as_view(template_name="portal/index.html"), name='password_reset_confirm'),
]

#if settings.DEBUG:
#    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)