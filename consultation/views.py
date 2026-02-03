from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.core.paginator import Paginator  # Import pour la pagination
from administration.models import Patient, AnalyseIA 
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
    """Interface de consultation : RDV du jour, recherche et liste globale avec pagination"""
    maintenant = timezone.now()
    aujourdhui = maintenant.date()
    
    # --- LOGIQUE DE RECHERCHE ---
    query = request.GET.get('search', '')
    if query:
        # Recherche par nom complet OU par code anonyme
        liste_patients = Patient.objects.filter(
            Q(nom_complet__icontains=query) | Q(code_anonyme__icontains=query)
        ).order_by('-date_creation')
    else:
        liste_patients = Patient.objects.all().order_by('-date_creation')

    # --- LOGIQUE DE PAGINATION (10 patients par page) ---
    paginator = Paginator(liste_patients, 10)
    page_number = request.GET.get('page')
    patients_pagines = paginator.get_page(page_number)

    # --- FILTRAGE DES RDV ---
    mes_rdv = RendezVous.objects.filter(
        medecin=request.user, 
        date_rdv__date=aujourdhui
    ).select_related('patient').order_by('date_rdv')

    if not mes_rdv.exists():
        mes_rdv = RendezVous.objects.filter(
            medecin=request.user,
            statut='PREVU'
        ).select_related('patient').order_by('date_rdv')

    # --- LOGIQUE DU BADGE (Uniquement les analyses NON LUES) ---
    analyses_du_jour = [
        str(id_p) for id_p in AnalyseIA.objects.filter(
            consulte_par_medecin=False
        ).values_list('scan__patient_id', flat=True)
    ]

    return render(request, 'dashboards/medecin.html', {
        'rdv': mes_rdv,
        'nb_rdv': mes_rdv.count(),
        'patients': patients_pagines,  # On envoie l'objet paginé
        'analyses_du_jour': analyses_du_jour,
        'date_serveur': aujourdhui,
        'search_query': query
    })

# 3. ACTION : EFFECTUER LA CONSULTATION
@login_required
@user_passes_test(est_medecin)
def effectuer_consultation(request, rdv_id):
    """Page de saisie des notes cliniques avec historique des scans"""
    rdv = get_object_or_404(RendezVous, pk=rdv_id)
    
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

# 4. DOSSIER MÉDICAL
@login_required
@user_passes_test(est_medecin)
def detail_patient(request, patient_id):
    """Affiche le dossier médical et marque les notifications comme lues"""
    patient = get_object_or_404(Patient, pk=patient_id)
    
    # Marquer comme lu
    AnalyseIA.objects.filter(scan__patient=patient, consulte_par_medecin=False).update(consulte_par_medecin=True)
    
    try:
        historique_rdv = patient.rendezvous.all().order_by('-date_rdv')
    except AttributeError:
        historique_rdv = patient.rendezvous_set.all().order_by('-date_rdv')
    
    try:
        scans = patient.scans.all().order_by('-date_upload')
    except AttributeError:
        scans = patient.scannerct_set.all().order_by('-date_upload')

    return render(request, 'dashboards/detail_patient.html', {
        'patient': patient,
        'historique': historique_rdv,
        'scans': scans
    })