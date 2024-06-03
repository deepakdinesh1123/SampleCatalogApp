from django.urls import re_path

from .views import FrameRouterView


urlpatterns = [
    re_path(r"^/$", FrameRouterView.as_view(), name="frame"),
]
