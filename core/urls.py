
from django.conf import settings
from django.urls import path
from core import views
from django.conf.urls.static import static


urlpatterns = [
    # authentication urls
    path('', views.login_view, name='login'),
    path('register', views.register_view, name='register'),

    # dashboard urls
    path('dashboard', views.dashboard, name='dashboard'),
    path('properties', views.properties, name='properties'),

    # logout
    path('logout', views.logout_view, name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)