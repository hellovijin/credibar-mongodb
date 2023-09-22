from django.urls import path
from credi.views import *

app_name = "app_credi"

#views 
urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('email/<str:slug>/', EmailTemplateView.as_view(), name="email_template"),
]