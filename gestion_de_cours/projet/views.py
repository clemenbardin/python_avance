from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import InscriptionForm
from .models import Enrollment

def inscription_cours(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            cours = form.cleaned_data['cours']
            email = form.cleaned_data['email']
            motivation = form.cleaned_data.get('motivation', '')
            
            etudiant, created = User.objects.get_or_create(
                email=email,
                defaults={'username': email.split('@')[0]}
            )
            
            enrollment = Enrollment.objects.create(
                cours=cours,
                étudiant=etudiant,
                statut='en cours'
            )
            
            messages.success(
                request,
                f'Inscription réussie ! Vous êtes maintenant inscrit au cours "{cours.titre}".'
            )
            
            return redirect('liste_cours')
    else:
        form = InscriptionForm()
    
    return render(request, 'projet/inscription_cours.html', {'form': form})