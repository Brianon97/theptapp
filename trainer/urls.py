# trainer/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.booking_list, name='booking_list'),
    path('new/', views.booking_create, name='booking_create'),
    path('signup/', views.signup, name='signup'),
]

