from django.urls import path

from .views import create, read, update, delete

urlpatterns = [
    path('create/timeline', create.create_timeline),
    path('create/screener', create.create_screener),
    path('create/screener_application', create.create_screener_application),
    path('read/timeline_list', read.read_timeline_list),
    path('read/screener_list', read.read_screener_list),
    path('read/screener_application_list', read.read_screener_application_list),
    path('read/segment_list', read.read_segment_list),
]
