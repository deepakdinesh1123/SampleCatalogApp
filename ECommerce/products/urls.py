from .views import EnquiryCrudView, ProductCrudView
from django.urls import path

urlpatterns = [
    path(
        "index/",
        ProductCrudView.as_view(),
    ),
    path("enquiries/", EnquiryCrudView.as_view()),
]
