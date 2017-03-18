from django.conf.urls import url

from . import views
from .models import Roommate

urlpatterns = [
    url(r'^$', views.index, name='index'),
]
