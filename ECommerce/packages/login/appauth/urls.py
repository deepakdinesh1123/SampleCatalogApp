"""Defines which API URLs."""
from django.urls import re_path

from .views import AppUserLoginView


urlpatterns = [
    re_path(r"^/$", AppUserLoginView.as_view()),
]
