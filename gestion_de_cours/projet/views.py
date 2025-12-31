from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from .forms import InscriptionForm
from .models import Enrollment, Course

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

def login_view(request):
    if request.user.is_authenticated:
        return redirect('accueil')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, 'Veuillez remplir tous les champs.')
            return render(request, 'projet/login.html')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenue {user.username} !')
            return redirect('accueil')
        else:
            messages.error(
                request,
                'Nom d\'utilisateur ou mot de passe incorrect.'
            )
    
    return render(request, 'projet/login.html')

@login_required
def accueil(request):
    return render(request, 'projet/accueil.html', {
        'user': request.user
    })

def liste_cours(request):
    """Vue pour afficher la liste des cours publiés"""
    cours = Course.objects.filter(statut='publié')
    return render(request, 'projet/liste_cours.html', {'cours': cours})

def logout_view(request):
    """Vue pour déconnecter l'utilisateur"""
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('login')

@login_required
@permission_required('projet.can_publish_course', raise_exception=True)
def course_publish(request, course_id):
    """
    Vue pour publier un cours (changer le statut de 'brouillon' à 'publié')
    Nécessite l'authentification et la permission can_publish_course
    """
    # Récupérer le cours ou retourner 404
    cours = get_object_or_404(Course, id=course_id)
    
    # Vérifier que le cours est en brouillon
    if cours.statut != 'brouillon':
        messages.error(
            request,
            f'Le cours "{cours.titre}" ne peut pas être publié. Statut actuel : {cours.get_statut_display()}.'
        )
        return redirect('liste_cours')
    
    # Changer le statut à 'publié'
    cours.statut = 'publié'
    cours.save()
    
    messages.success(
        request,
        f'Le cours "{cours.titre}" a été publié avec succès !'
    )
    
    return redirect('liste_cours')