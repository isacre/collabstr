from django.urls import path

from .views import GenerateBriefView

urlpatterns = [
    path("generate-brief/", GenerateBriefView.as_view(), name="generate-brief"),
]
