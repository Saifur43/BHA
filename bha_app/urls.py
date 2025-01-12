from django.urls import path
from . import views

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('components/', views.BHAComponentListView.as_view(), name='component_list'),
    path('components/create/', views.BHAComponentCreateView.as_view(), name='component_create'),
    path('components/<int:pk>/edit/', views.BHAComponentEditView.as_view(), name='component_edit'),
    path('components/<int:pk>/delete/', views.BHAComponentDeleteView.as_view(), name='component_delete'),
    path('configuration/create/', views.BHAConfigurationCreateView.as_view(), name='configuration_create'),
    path('configuration/<int:pk>/', views.BHAConfigurationDetailView.as_view(), name='configuration_detail'),
]