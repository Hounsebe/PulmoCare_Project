import io
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta, date
from django.http import FileResponse

# Imports pour ReportLab
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

from administration.models import Patient, ScannerCT, AnalyseIA

# --- PERMISSIONS ---
def est_radiologue(user):
    return user.is_authenticated and hasattr(user, 'service') and user.service == 'RADIO'

# --- 1. LE DASHBOARD ---
@login_required
@user_passes_test(est_radiologue)
def dashboard_radiologie(request):
    query = request.GET.get('search', '')
    if query:
        liste_scans = ScannerCT.objects.filter(
            patient__code_anonyme__icontains=query
        ).select_related('patient', 'resultat').order_by('-date_upload')
    else:
        liste_scans = ScannerCT.objects.select_related('patient', 'resultat').all().order_by('-date_upload')
    
    paginator = Paginator(liste_scans, 10)
    page_number = request.GET.get('page')
    scans_pagines = paginator.get_page(page_number)

    aujourdhui = timezone.now().date()
    tous_les_scans = ScannerCT.objects.all()
    stats = {
        'total_aujourdhui': tous_les_scans.filter(date_upload__date=aujourdhui).count(),
        'non_analyses': tous_les_scans.filter(resultat__isnull=True).count(),
        'benins': tous_les_scans.filter(resultat__score_malignite__lte=0.6).count(),
        'alertes': tous_les_scans.filter(resultat__score_malignite__gt=0.6).count(),
    }
    
    return render(request, 'dashboards/radiologie.html', {
        'scans': scans_pagines,
        'stats': stats,
        'search_query': query,
    })

# --- 2. LA VUE ANALYTIQUE ---
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
    scan = get_object_or_404(ScannerCT, pk=scan_id)
    analyse, created = AnalyseIA.objects.get_or_create(scan=scan)
    analyse.simuler_ia()
    
    if analyse.score_malignite > 0.8:
        messages.error(request, f"ALERTE CRITIQUE : Scan {scan.patient.code_anonyme} (Score: {analyse.score_malignite})")
    else:
        messages.success(request, f"Analyse terminée pour {scan.patient.code_anonyme}")

    return redirect('dashboard_radiologie')

# --- 4. ACTION : GÉNÉRER RAPPORT PDF ---
@login_required
@user_passes_test(est_radiologue)
def generer_rapport_pdf(request, scan_id):
    scan = get_object_or_404(ScannerCT, pk=scan_id)
    
    if not hasattr(scan, 'resultat'):
        messages.error(request, "Veuillez d'abord effectuer l'analyse IA.")
        return redirect('dashboard_radiologie')

    # Calcul de l'âge à partir de date_naissance
    aujourdhui = date.today()
    naissance = scan.patient.date_naissance
    age = aujourdhui.year - naissance.year - ((aujourdhui.month, aujourdhui.day) < (naissance.month, naissance.day))

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    largeur, hauteur = A4

    # En-tête
    p.setFont("Helvetica-Bold", 18)
    p.drawString(50, hauteur - 50, "PULMOCARE - RAPPORT D'ANALYSE IA")
    p.setFont("Helvetica", 10)
    p.drawString(50, hauteur - 65, f"Date du rapport : {timezone.now().strftime('%d/%m/%Y %H:%M')}")
    p.line(50, hauteur - 75, 550, hauteur - 75)

    # Section Patient
    p.setFont("Helvetica-Bold", 13)
    p.drawString(50, hauteur - 110, "IDENTITÉ DU PATIENT")
    p.setFont("Helvetica", 11)
    p.drawString(60, hauteur - 130, f"Nom complet : {scan.patient.nom_complet}")
    p.drawString(60, hauteur - 150, f"ID Anonyme : {scan.patient.code_anonyme}")
    # Correction Sexe & Age basés sur votre modèle
    p.drawString(60, hauteur - 170, f"Genre : {scan.patient.get_genre_display()}")
    p.drawString(60, hauteur - 190, f"Âge : {age} ans")

    # Section IA
    p.setFont("Helvetica-Bold", 13)
    p.drawString(50, hauteur - 230, "RÉSULTATS DE L'ALGORITHME IA")
    
    score = scan.resultat.score_malignite
    p.setFont("Helvetica-Bold", 14)
    
    if score > 0.6:
        p.setFillColor(colors.red)
        conclusion = "ALERTE : HAUTE PROBABILITÉ DE MALIGNITÉ"
    else:
        p.setFillColor(colors.green)
        conclusion = "STABLE : FAIBLE PROBABILITÉ DE MALIGNITÉ"

    p.drawString(60, hauteur - 260, f"Score de malignité : {score * 100}%")
    p.drawString(60, hauteur - 285, f"Conclusion IA : {conclusion}")

    # Détails techniques (issus du JSONField de votre modèle)
    p.setFillColor(colors.black)
    p.setFont("Helvetica", 11)
    details = scan.resultat.details_nodules or {}
    p.drawString(60, hauteur - 320, f"Nodules détectés : {details.get('nodules_detectes', 'N/A')}")
    p.drawString(60, hauteur - 340, f"Zone critique : {details.get('zone_critique', 'N/A')}")

    # Pied de page
    p.setFont("Helvetica-Oblique", 8)
    p.drawString(50, 40, "Ce document est une aide au diagnostic. La signature du radiologue est requise pour validation.")

    p.showPage()
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f"Rapport_{scan.patient.code_anonyme}.pdf")