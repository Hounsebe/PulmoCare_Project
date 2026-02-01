from django.conf import settings
from django.db import models
from administration.models import Patient # On importe le Patient du service admin

class RendezVous(models.Model):
    STATUT_CHOICES = [
        ('PREVU', 'Prévu'),
        ('TERMINE', 'Terminé'),
        ('ANNULE', 'Annulé'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='rendezvous')
    medecin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'service': 'MEDECIN'})
    date_rdv = models.DateTimeField()
    motif = models.TextField(blank=True, null=True)
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='PREVU')
    notes_medicales = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"RDV de {self.patient.code_anonyme} le {self.date_rdv.strftime('%d/%m/%Y')}"