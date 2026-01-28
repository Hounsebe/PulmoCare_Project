from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
import random

# ==========================================
# 1. SERVICE AUTHENTIFICATION (Utilisateurs)
# ==========================================
class Utilisateur(AbstractUser):
    """
    Modèle personnalisé pour gérer les différents métiers de la clinique.
    """
    SERVICES = [
        ('ADMIN', 'Administration / Accueil'),
        ('MEDECIN', 'Consultation / Médecine'),
        ('RADIO', 'Radiologie / IA'),
    ]
    service = models.CharField(max_length=10, choices=SERVICES, default='ADMIN')
    matricule = models.CharField(max_length=20, unique=True, null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.get_service_display()})"

# ==========================================
# 2. SERVICE ADMINISTRATION (Identité)
# ==========================================
class Patient(models.Model):
    """
    Table centrale pour l'identification des patients.
    """
    id_patient = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code_anonyme = models.CharField(max_length=50, unique=True, help_text="ID pour l'IA")
    nom_complet = models.CharField(max_length=150)
    date_naissance = models.DateField()
    genre = models.CharField(max_length=1, choices=[('M', 'Masculin'), ('F', 'Féminin')])
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom_complet} - {self.code_anonyme}"

# ==========================================
# 3. SERVICE CONSULTATION (Données Cliniques)
# ==========================================
class ProfilClinique(models.Model):
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name='profil')
    tabac_score = models.IntegerField(default=0, help_text="Paquets/Année")
    exposition_toxique = models.BooleanField(default=False)
    antecedents_familiaux = models.BooleanField(default=False)

class Biomarqueur(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='biomarqueurs')
    date_examen = models.DateField(auto_now_add=True)
    taux_CEA = models.FloatField(verbose_name="Antigène Carcino-Embryonnaire (ng/mL)")
    taux_CYFRA21 = models.FloatField(verbose_name="CYFRA 21-1 (ng/mL)")

# ==========================================
# 4. SERVICE RADIOLOGIE & IA (Imagerie)
# ==========================================
class ScannerCT(models.Model):
    id_scan = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='scans')
    image_dicom = models.FileField(upload_to='scanners/%Y/%m/%d/')
    date_upload = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Scan {self.id_scan} - Patient {self.patient.code_anonyme}"

class AnalyseIA(models.Model):
    scan = models.OneToOneField(ScannerCT, on_delete=models.CASCADE, related_name='resultat')
    score_malignite = models.FloatField(null=True, blank=True) # Entre 0 et 1
    details_nodules = models.JSONField(null=True, blank=True) # Liste des coordonnées
    date_analyse = models.DateTimeField(auto_now_add=True)
    avis_medecin = models.TextField(blank=True)
    est_valide = models.BooleanField(default=False)

    def simuler_ia(self):
        """
        Le Coeur du Projet : Simule l'exécution de l'algorithme IA
        """
        # Génère un score entre 0.1 et 0.95
        self.score_malignite = round(random.uniform(0.1, 0.95), 2)
        
        # Simulation de détection d'objets (nodules)
        self.details_nodules = {
            "statut": "Analyse Complétée",
            "nodules_detectes": random.randint(0, 4),
            "zone_critique": random.choice(["Lobe Supérieur Gauche", "Lobe Inférieur Droit", "Aucune"]),
            "niveau_confiance": f"{random.randint(85, 99)}%"
        }
        self.save()

    @property
    def interpretation_score(self):
        if self.score_malignite is None: return "Non analysé"
        if self.score_malignite < 0.3: return "Faible risque"
        if self.score_malignite < 0.6: return "Risque Modéré"
        return "Risque Élevé"