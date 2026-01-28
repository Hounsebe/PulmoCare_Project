from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from administration.models import Patient, ScannerCT, AnalyseIA

# ==========================================
# 1. PERMISSIONS
# ==========================================
def est_radiologue(user):
    return user.is_authenticated and user.service == 'RADIO'

# ==========================================
# 2. VUES DU DASHBOARD
# ==========================================

@login_required
@user_passes_test(est_radiologue)
def dashboard_radiologie(request):
    """Interface technique pour l'upload et l'analyse IA"""
    # On récupère les scanners car c'est ce que l'IA analyse, 
    # tout en liant le patient et le résultat pour éviter trop de requêtes SQL
    scans = ScannerCT.objects.select_related('patient', 'resultat').all().order_by('-date_upload')
    
    return render(request, 'dashboards/radiologie.html', {
        'scans': scans
    })

@login_required
@user_passes_test(est_radiologue)
def lancer_analyse(request, scan_id):
    """
    Vue pivot : C'est ici que l'IA est déclenchée sur un scan précis.
    """
    # 1. Récupérer le scan
    scan = get_object_or_404(ScannerCT, pk=scan_id)
    
    # 2. Créer l'entrée AnalyseIA si elle n'existe pas, puis lancer la simulation
    analyse, created = AnalyseIA.objects.get_or_create(scan=scan)
    
    # 3. Appel du "Coeur du projet" (méthode définie dans models.py)
    analyse.simuler_ia()
    
    # 4. Rediriger vers le dashboard pour voir le résultat mis à jour
    return redirect('dashboard_radiologie')