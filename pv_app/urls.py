from django.urls import path
from .views import *
urlpatterns=[
    path('',home,name='home'),
    path('map/',map_view,name='map'),
    path('pv_tracking/<str:track_type>/',PVTrackingView.as_view(),name='pv_tracking'),
    path('get-address-suggestions/', get_address_suggestions, name='get_address_suggestions'),
]