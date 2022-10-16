from django.urls import path

from . import views

urlpatterns = [
    path('create_strategist', views.create_strategist),
    path('get_strategist_list', views.get_strategist_list),
    path('create_filter', views.create_filter),
    path('apply_filter_to_strategist', views.apply_filter_to_strategist)
]
