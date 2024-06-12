from django.urls import path
from .views import register, cancel, succeed
from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', register, name='register'),
    path('succeed', succeed, name='succeed'),
    path('cancel', cancel, name='cancel'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
