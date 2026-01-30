from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from administration.models import Patient, ScannerCT, AnalyseIA
from django.utils import timezone
from django.db.models import Count
from datetime import timedelta

# --- PERMISSIONS ---
def est_radiologue(user):
    return user.is_authenticated and hasattr(user, 'service') and user.service == 'RADIO'

# --- 1. LE DASHBOARD (Tableau et Cartes) ---
@login_required
@user_passes_test(est_radiologue)
def dashboard_radiologie(request):
    scans = ScannerCT.objects.select_related('patient', 'resultat').all().order_by('-date_upload')
    aujourdhui = timezone.now().date()
    
    stats = {
        'total_aujourdhui': scans.filter(date_upload__date=aujourdhui).count(),
        'non_analyses': scans.filter(resultat__isnull=True).count(),
        'benins': scans.filter(resultat__score_malignite__lte=0.6).count(),
        'alertes': scans.filter(resultat__score_malignite__gt=0.6).count(),
    }
    
    return render(request, 'dashboards/radiologie.html', {
        'scans': scans,
        'stats': stats,
    })

# --- 2. LA VUE ANALYTIQUE (La Courbe seule) ---
@login_required
@user_passes_test(est_radiologue)
def analytique_radiologie(request):
    aujourdhui = timezone.now().date()
    jours_labels = []
    donnees_scans = []
    
    for i in range(6, -1, -1):
        date_cible = aujourdhui - timedelta(days=i)
        jours_labels.append(date_cible.strftime('%d/%m'))
        count = ScannerCT.objects.filter(date_upload__date=date_cible).count()
        donnees_scans.append(count)
    
    return render(request, 'dashboards/analytics.html', {
        'jours_labels': jours_labels,
        'donnees_scans': donnees_scans,
    })

# --- 3. ACTION : LANCER L'IA ---
@login_required
@user_passes_test(est_radiologue)
def lancer_analyse(request, scan_id):
    """Déclenche la simulation IA sur un scan"""
    scan = get_object_or_404(ScannerCT, pk=scan_id)
    # Récupère l'analyse existante ou la crée
    analyse, created = AnalyseIA.objects.get_or_create(scan=scan)
    # Lance la méthode de calcul définie dans models.py
    analyse.simuler_ia()
    return redirect('dashboard_radiologie')