from django.urls import path

from . import views

urlpatterns = [
    path('prepare', views.prepare),
    path('update', views.update),
]
