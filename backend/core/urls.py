from django.urls import path

from . import views

urlpatterns = [
    path('calculate_segment_list', views.calculate_segment_list),
]
