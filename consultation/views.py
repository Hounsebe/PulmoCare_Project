from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from administration.models import Patient # Importation depuis le service source

def est_medecin(user):
    return user.is_authenticated and user.service == 'MEDECIN'

@login_required
@user_passes_test(est_medecin)
def dashboard_consultation(request):
    """Interface de consultation des dossiers patients"""
    # Le médecin consulte la liste des patients
    patients = Patient.objects.all().order_by('-date_creation')
    return render(request, 'dashboards/medecin.html', {'patients': patients})