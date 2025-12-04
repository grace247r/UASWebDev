from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search_flight, name='search'),
    path('results/', views.flight_result, name='results'),
    path('booking/', views.flight_booking, name='booking'),
    path('api/city-search/', views.city_search, name='city_search'),
]
