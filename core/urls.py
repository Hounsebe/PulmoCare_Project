from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Importation segmentée par service
from administration.views import ConnexionClinique, dashboard_admin
from consultation.views import dashboard_consultation
from radiologie_ia.views import dashboard_radiologie

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # SERVICE AUTH (Administration)
    path('login/', ConnexionClinique.as_view(), name='login'),
    path('dashboard/admin/', dashboard_admin, name='dashboard_admin'),
    
    # SERVICE CLINIQUE (Consultation)
    path('dashboard/medecin/', dashboard_consultation, name='dashboard_consultation'),
    
    # SERVICE DIAGNOSTIC (Radiologie IA)
    path('dashboard/radiologie/', dashboard_radiologie, name='dashboard_radiologie'),
    
    path('accounts/', include('django.contrib.auth.urls')),
]

# SOA : Permettre l'accès partagé aux images scanner
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)