from django.urls import path

from . import views

urlpatterns = [
    path('create_strategist', views.create_strategist),
    path('get_strategist_list', views.get_strategist_list),
    path('get_filter_list', views.get_filter_list),
    path('create_filter', views.create_filter),
    path('register_filter_to_strategist', views.register_filter_to_strategist),
    path('calculate_segment_list', views.calculate_segment_list)
]
