from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# 1. Importations pour le service ADMINISTRATION / AUTH
from administration.views import ConnexionClinique, dashboard_admin

# 2. Importations pour le service CLINIQUE (Consultation)
from consultation.views import (
    dashboard_consultation, 
    effectuer_consultation,
    detail_patient
)

# 3. Importations pour le service DIAGNOSTIC (Radiologie IA)
from radiologie_ia.views import (
    dashboard_radiologie, 
    lancer_analyse, 
    analytique_radiologie,
    generer_rapport_pdf  # <--- AJOUTÉ ICI
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --- SERVICE AUTH & ADMIN ---
    path('login/', ConnexionClinique.as_view(), name='login'),
    path('dashboard/admin/', dashboard_admin, name='dashboard_admin'),
    
    # --- SERVICE CLINIQUE (Médecin) ---
    path('dashboard/medecin/', dashboard_consultation, name='dashboard_consultation'),
    path('dashboard/medecin/consulter/<int:rdv_id>/', effectuer_consultation, name='effectuer_consultation'),
    path('dashboard/medecin/patient/<uuid:patient_id>/', detail_patient, name='detail_patient'),
    
    # --- SERVICE DIAGNOSTIC (Radiologie) ---
    path('dashboard/radiologie/', dashboard_radiologie, name='dashboard_radiologie'),
    path('dashboard/radiologie/stats/', analytique_radiologie, name='analytique_radiologie'),
    path('dashboard/radiologie/analyser/<uuid:scan_id>/', lancer_analyse, name='lancer_analyse'),
    
    # --- GÉNÉRATION DE RAPPORT ---
    path('dashboard/radiologie/pdf/<uuid:scan_id>/', generer_rapport_pdf, name='generer_pdf'), # <--- NOUVELLE ROUTE
    
    # Auth Django par défaut
    path('accounts/', include('django.contrib.auth.urls')),
]

# Accès aux fichiers MEDIA (Scanners) en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)