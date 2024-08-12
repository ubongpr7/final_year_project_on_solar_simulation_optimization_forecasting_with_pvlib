from django.urls import path
from .views import *
urlpatterns=[
    path('',home,name='home'),
    path('map/',map_view,name='map'),
    path('pv_tracking/<str:track_type>/',PVTrackingView.as_view(),name='pv_tracking'),
    path('get-address-suggestions/', get_address_suggestions, name='get_address_suggestions'),

    # path('upload/', DataUploadView.as_view(), name='upload_data'),
    # path('plot_data/', plot_data_view, name='plot_data'),
    # path('view-sample/', ViewSampleDataView.as_view(), name='view_sample_data'),
    # # path('clean-and-visualize/', CleanAndVisualizeView.as_view(), name='clean_and_visualize'),
    # path('clean-and-visualize/', get_columns_view, name='clean_and_visualize'),


]