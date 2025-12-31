from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import Course, Enrollment

class InscriptionForm(forms.Form):
    cours = forms.ModelChoiceField(
        queryset=Course.objects.filter(statut='publié'),
        label="Cours",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    email = forms.EmailField(
        label="Email de l'étudiant",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'exemple@student.edu'})
    )
    
    motivation = forms.CharField(
        label="Motivation",
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Expliquez pourquoi vous souhaitez suivre ce cours...'
        })
    )
    
    acceptation_conditions = forms.BooleanField(
        label="J'accepte les conditions d'inscription",
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and not email.endswith('@student.edu'):
            raise ValidationError(
                "L'email doit appartenir au domaine @student.edu"
            )
        return email
    
    def clean_cours(self):
        cours = self.cleaned_data.get('cours')
        if cours:
            nombre_inscriptions = cours.enrollments.count()
            if nombre_inscriptions >= 30:
                raise ValidationError(
                    f"Ce cours est complet (30 étudiants maximum). Actuellement : {nombre_inscriptions} étudiants."
                )
        return cours
    
    def clean(self):
        cleaned_data = super().clean()
        cours = cleaned_data.get('cours')
        email = cleaned_data.get('email')
        
        if cours and email:
            try:
                etudiant = User.objects.get(email=email)
                if Enrollment.objects.filter(cours=cours, étudiant=etudiant).exists():
                    raise ValidationError(
                        f"L'étudiant avec l'email {email} est déjà inscrit à ce cours."
                    )
            except User.DoesNotExist:
                pass
        
        return cleaned_data