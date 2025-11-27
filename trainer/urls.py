# trainer/urls.py
from django.urls import path
from . import views

app_name = 'trainer'

urlpatterns = [
    path('', views.booking_list, name='booking_list'),
    path('new/', views.booking_create, name='booking_create'),
    path('<int:pk>/edit/', views.booking_edit, name='booking_edit'),
    path('<int:pk>/delete/', views.booking_delete, name='booking_delete'),
    path('signup/', views.signup, name='signup'),

]

