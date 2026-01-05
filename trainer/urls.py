# trainer/urls.py
from django.urls import path
from . import views

app_name = 'trainer'

urlpatterns = [
    path('bookings/', views.booking_list, name='booking_list'),
    path('new/', views.booking_create, name='booking_create'),
    path('<int:pk>/edit/', views.booking_edit, name='booking_edit'),
    path('<int:pk>/delete/', views.booking_delete, name='booking_delete'),
    path('client/<int:user_id>/', views.client_detail,
         name='client_detail'),
    path('signup/', views.signup, name='signup'),
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/check/', views.check_notifications,
         name='check_notifications'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
]




