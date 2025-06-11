
from django.conf import settings
from django.urls import path
from core import views
from django.conf.urls.static import static


urlpatterns = [
    path('', views.login, name='index'),
    path('', views.login, name='profile'),
    path('register', views.register_view, name='register'),
    path('', views.login, name='login'),
    path('', views.login, name='password_reset'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)