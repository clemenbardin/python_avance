"""
Script pour créer un utilisateur Django
Exécutez : python create_user.py
"""
import os
import django

# Configuration de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_de_cours.settings')
django.setup()

from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from projet.models import Course

# Créer un superutilisateur
username = 'admin'
email = 'admin@example.com'
password = 'admin123'

if User.objects.filter(username=username).exists():
    print(f"L'utilisateur '{username}' existe déjà.")
    user = User.objects.get(username=username)
else:
    user = User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Superutilisateur '{username}' créé avec succès !")

# Attribuer la permission can_publish_course
content_type = ContentType.objects.get_for_model(Course)
permission = Permission.objects.get(
    codename='can_publish_course',
    content_type=content_type
)
user.user_permissions.add(permission)
print(f"Permission 'can_publish_course' attribuée à '{username}'.")

print("\n" + "="*50)
print("Identifiants de connexion :")
print(f"Username: {username}")
print(f"Password: {password}")
print("="*50)

