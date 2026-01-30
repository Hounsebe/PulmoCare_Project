from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Importation segmentée par service
from administration.views import ConnexionClinique, dashboard_admin
from consultation.views import dashboard_consultation

# Importations pour le service Radiologie (On ajoute analytique_radiologie)
from radiologie_ia.views import (
    dashboard_radiologie, 
    lancer_analyse, 
    analytique_radiologie
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # SERVICE AUTH (Administration)
    path('login/', ConnexionClinique.as_view(), name='login'),
    path('dashboard/admin/', dashboard_admin, name='dashboard_admin'),
    
    # SERVICE CLINIQUE (Consultation)
    path('dashboard/medecin/', dashboard_consultation, name='dashboard_consultation'),
    
    # SERVICE DIAGNOSTIC (Radiologie IA)
    # 1. Le Dashboard principal (Tableau)
    path('dashboard/radiologie/', dashboard_radiologie, name='dashboard_radiologie'),
    
    # 2. La page des statistiques (Graphique)
    path('dashboard/radiologie/stats/', analytique_radiologie, name='analytique_radiologie'),
    
    # 3. Action de traitement IA
    path('dashboard/radiologie/analyser/<uuid:scan_id>/', lancer_analyse, name='lancer_analyse'),
    
    path('accounts/', include('django.contrib.auth.urls')),
]

# Accès aux images scanner (Média)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)