from django.urls import path
from users.views import *
from users.api import *

app_name = "app_users"

#views 
urlpatterns = []

#api
urlpatterns += [
    path('api/account/signup/basic-information/', AccountAPI.as_view({'post': 'signup_basic_information'}), name="api_signup_basic_information"),
    path('api/account/signup/verification/<str:user>/<str:token>/', AccountAPI.as_view({'post': 'signup_verification'}), name="api_signup_verification"),
    path('api/account/signup/documents/', AccountAPI.as_view({'post': 'signup_documents'}), name="api_signup_documents"),
    path('api/account/signup/additional-information/', AccountAPI.as_view({'post': 'signup_additional_information'}), name="api_signup_additional_information"),
    path('api/account/signup/password/', AccountAPI.as_view({'post': 'signup_password'}), name="api_signup_password"),
    path('api/account/signin/', AccountAPI.as_view({'post': 'signin'}), name="api_signin"),
]