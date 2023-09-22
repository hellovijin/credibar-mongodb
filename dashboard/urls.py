from django.urls import path
from dashboard.views import *
from dashboard.api import *

app_name = "app_dashboard"

#views 
urlpatterns = []

#api
urlpatterns += [
    #user designation
    path('api/user/designation/', UserDesignationAPI.as_view({'get': 'list', 'post': 'create'}), name="api_user_designation"),
    path('api/user/designation/<int:pk>/', UserDesignationAPI.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name="api_user_designation"),
]