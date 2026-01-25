from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Patient

class ConnexionClinique(LoginView):
    """Vue pour l'authentification des utilisateurs"""
    template_name = 'registration/login.html'
    
    def get_success_url(self):
        """Redirige l'utilisateur vers son dashboard selon son service"""
        user = self.request.user
        if user.service == 'ADMIN':
            return reverse_lazy('dashboard_admin')
        elif user.service == 'MEDECIN':
            return reverse_lazy('dashboard_consultation')
        elif user.service == 'RADIO':
            return reverse_lazy('dashboard_radiologie')
        return reverse_lazy('login')

# Vues temporaires pour éviter d'autres erreurs d'URL
def dashboard_admin(request):
    return render(request, 'dashboards/admin.html')

def dashboard_consultation(request):
    return render(request, 'dashboards/medecin.html')

def est_radiologue(user):
    return user.is_authenticated and user.service == 'RADIO'

@login_required
@user_passes_test(est_radiologue)
def dashboard_radiologie(request):
    # On récupère tous les patients pour les afficher au radiologue
    patients = Patient.objects.all().order_by('-date_creation')
    return render(request, 'dashboards/radiologie.html', {'patients': patients})