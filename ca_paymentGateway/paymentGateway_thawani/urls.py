from django.urls import path
from .views import register, cancel, done
from base64 import urlsafe_b64decode
from cgitb import handler
from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', register, name='register'),
    #path('/success/', success, name='success'),  # Add this line
    path('done', done, name='done'),  # Add this line
    path('cancel', cancel, name='cancel'),  # Add this line


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
