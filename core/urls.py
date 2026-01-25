"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from administration.views import (
    ConnexionClinique, 
    dashboard_admin, 
    dashboard_consultation, 
    dashboard_radiologie
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', ConnexionClinique.as_view(), name='login'),
    
    # Chemins de redirection
    path('dashboard/admin/', dashboard_admin, name='dashboard_admin'),
    path('dashboard/medecin/', dashboard_consultation, name='dashboard_consultation'),
    path('dashboard/radiologie/', dashboard_radiologie, name='dashboard_radiologie'),
    
    # Inclusion des URLs par défaut de l'auth (logout, etc.)
    path('accounts/', include('django.contrib.auth.urls')),
]