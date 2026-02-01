from django import forms
from .models import RendezVous

class ConsultationForm(forms.ModelForm):
    class Meta:
        model = RendezVous
        fields = ['notes_medicales', 'statut']
        widgets = {
            'notes_medicales': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Saisissez vos observations cliniques ici...'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
        }