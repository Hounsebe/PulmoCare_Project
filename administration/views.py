from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

class ConnexionClinique(LoginView):
    """Service d'authentification centralisé"""
    template_name = 'registration/login.html'
    
    def get_success_url(self):
        user = self.request.user
        # Le routage vers les autres services se fait ici
        if user.service == 'ADMIN':
            return reverse_lazy('dashboard_admin')
        elif user.service == 'MEDECIN':
            return reverse_lazy('dashboard_consultation')
        elif user.service == 'RADIO':
            return reverse_lazy('dashboard_radiologie')
        return reverse_lazy('login')

def dashboard_admin(request):
    """Portail de gestion des utilisateurs et du système"""
    return render(request, 'dashboards/admin.html')