from django.urls import path
from .views import *
urlpatterns=[
    path('',home,name='home'),
    path('map/',map_view,name='map'),
    path('pv_tracking/',PVTrackingView.as_view(),name='pv_tracking'),
    path('get-address-suggestions/', get_address_suggestions, name='get_address_suggestions'),

    # path('upload/', DataUploadView.as_view(), name='upload_data'),
    # path('plot_data/', plot_data_view, name='plot_data'),
    # path('view-sample/', ViewSampleDataView.as_view(), name='view_sample_data'),
    # # path('clean-and-visualize/', CleanAndVisualizeView.as_view(), name='clean_and_visualize'),
    # path('clean-and-visualize/', get_columns_view, name='clean_and_visualize'),
    path('simulation/', SimulationInterfaceView.as_view(), name='simulation_interface'),
    path('list/<str:app_name>/<str:model_name>/', GenericListView.as_view(), name='generic_list'),
    path('detail/<str:app_name>/<str:model_name>/<int:pk>/', GenericDetailView.as_view(), name='generic_detail'),
    path('update/<str:app_name>/<str:model_name>/<int:pk>/', GenericUpdateView.as_view(), name='generic_update'),
    path('add/<str:app_name>/<str:model_name>/', GenericCreateView.as_view(), name='generic_create'),
    path('delete/<str:app_name>/<str:model_name>/<int:pk>/', dynamic_delete, name='generic_delete'),
]