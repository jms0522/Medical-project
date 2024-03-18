from django.urls import path
from . import views

app_name = 'api_app'

urlpatterns = [
    path('map/', views.map, name='map'),
    path('pedia/', views.pedia, name='pedia'),
    path('search/', views.search_from_naver, name='search_from_naver'),
    path('ask/', views.ask, name='ask'),
]
