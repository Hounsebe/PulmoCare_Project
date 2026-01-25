from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur, Patient, ProfilClinique, Biomarqueur, ScannerCT, AnalyseIA

# Configuration de l'affichage de l'Utilisateur dans l'admin
class UtilisateurAdmin(UserAdmin):
    # On ajoute notre champ "service" à l'affichage de l'admin
    fieldsets = UserAdmin.fieldsets + (
        ('Informations Professionnelles', {'fields': ('service', 'matricule')}),
    )
    list_display = ['username', 'email', 'service', 'is_staff']

# Enregistrement des modèles
admin.site.register(Utilisateur, UtilisateurAdmin)
admin.site.register(Patient)
admin.site.register(ProfilClinique)
admin.site.register(Biomarqueur)
admin.site.register(ScannerCT)
admin.site.register(AnalyseIA)