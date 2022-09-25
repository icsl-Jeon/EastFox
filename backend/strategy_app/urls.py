from django.urls import path

from . import views

urlpatterns = [
    path('', views.connect_check, name='connection_check'),
    path('create_strategist', views.create_strategist, name='create_strategist'),
    path('apply_filter_to_strategist', views.apply_filter_to_strategist, name='apply_filter_to_strategist'),
]