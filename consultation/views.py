from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from administration.models import Patient 
from .models import RendezVous
from .forms import ConsultationForm
from django.utils import timezone

# 1. PERMISSION
def est_medecin(user):
    return user.is_authenticated and hasattr(user, 'service') and user.service == 'MEDECIN'

# 2. DASHBOARD GÉNÉRAL
@login_required
@user_passes_test(est_medecin)
def dashboard_consultation(request):
    """Interface de consultation : RDV du jour et liste globale"""
    maintenant = timezone.now()
    aujourdhui = maintenant.date()
    
    # Filtrage des RDV du jour
    mes_rdv = RendezVous.objects.filter(
        medecin=request.user, 
        date_rdv__date=aujourdhui
    ).select_related('patient').order_by('date_rdv')

    # Secours si aucun RDV aujourd'hui
    if not mes_rdv.exists():
        mes_rdv = RendezVous.objects.filter(
            medecin=request.user,
            statut='PREVU'
        ).select_related('patient').order_by('date_rdv')

    tous_les_patients = Patient.objects.all().order_by('-date_creation')

    return render(request, 'dashboards/medecin.html', {
        'rdv': mes_rdv,
        'nb_rdv': mes_rdv.count(),
        'patients': tous_les_patients,
        'date_serveur': aujourdhui
    })

# 3. ACTION : EFFECTUER LA CONSULTATION
@login_required
@user_passes_test(est_medecin)
def effectuer_consultation(request, rdv_id):
    """Page de saisie des notes cliniques avec historique des scans"""
    rdv = get_object_or_404(RendezVous, pk=rdv_id)
    
    # Récupération des scans (Service Radiologie)
    try:
        scans_patient = rdv.patient.scans.all().order_by('-date_upload')
    except AttributeError:
        scans_patient = rdv.patient.scannerct_set.all().order_by('-date_upload')

    if request.method == 'POST':
        form = ConsultationForm(request.POST, instance=rdv)
        if form.is_valid():
            consultation = form.save(commit=False)
            consultation.statut = 'TERMINE'
            consultation.save()
            return redirect('dashboard_consultation')
    else:
        form = ConsultationForm(instance=rdv)

    return render(request, 'dashboards/effectuer_consultation.html', {
        'form': form,
        'rdv': rdv,
        'scans': scans_patient
    })

# 4. DOSSIER MÉDICAL (Correction de l'indentation ici)
@login_required
@user_passes_test(est_medecin)
def detail_patient(request, patient_id):
    """Affiche le dossier médical historique d'un patient"""
    patient = get_object_or_404(Patient, id_patient=patient_id)
    
    # Récupérer l'historique des RDV
    try:
        historique_rdv = patient.rendezvous.all().order_by('-date_rdv')
    except AttributeError:
        historique_rdv = patient.rendezvous_set.all().order_by('-date_rdv')
    
    # Récupérer les scans et résultats d'IA
    try:
        scans = patient.scans.all().order_by('-date_upload')
    except AttributeError:
        scans = patient.scannerct_set.all().order_by('-date_upload')

    return render(request, 'dashboards/detail_patient.html', {
        'patient': patient,
        'historique': historique_rdv,
        'scans': scans
    })