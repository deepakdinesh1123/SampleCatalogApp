from django.urls import path
from .views import FrameConfigureAPI, FrameConfigureView


urlpatterns = [
     path(
        '/',
        FrameConfigureView.as_view(),
        name='frame-configure'
     ),
     path(
        'api/',
        FrameConfigureAPI.as_view(),
        name='frame'
    ),
]
