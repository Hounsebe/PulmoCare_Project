from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from administration.models import Patient 


def est_radiologue(user):
    return user.is_authenticated and user.service == 'RADIO'

@login_required
@user_passes_test(est_radiologue)
def dashboard_radiologie(request):
    """Interface technique pour l'upload et l'analyse IA"""
    patients = Patient.objects.all().order_by('-date_creation')
    return render(request, 'dashboards/radiologie.html', {'patients': patients})