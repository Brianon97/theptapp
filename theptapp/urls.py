# theptapp/urls.py  ← Replace the ENTIRE file with this

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Home page
    path('', TemplateView.as_view(template_name='home.html'), name='home'),

    # Login / logout
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),

    # ALL trainer URLs (new/, signup/, etc.)
    path('', include('trainer.urls', namespace='trainer')),
    
]