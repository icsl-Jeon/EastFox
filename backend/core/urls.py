from django.urls import path

from . import views

urlpatterns = [
    path('update_segment_list_for_timeline', views.update_segment_list_for_timeline),
]
