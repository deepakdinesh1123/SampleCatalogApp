from django.urls import re_path
from .views import LoginConfigureView, LoginConfigureAPIView


urlpatterns = [
    re_path("^/$", LoginConfigureView.as_view()),
    re_path("^api/$", LoginConfigureAPIView.as_view()),
]
