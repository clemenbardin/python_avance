from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.utils import timezone

class Instructor(models.Model):
    nom_complet = models.CharField(max_length=200, verbose_name="Nom complet")
    email = models.EmailField(unique=True, verbose_name="E-mail")
    biographie = models.TextField(verbose_name="Biographie", blank=True, null=True
    )
    photo_profil = models.ImageField(upload_to='instructors/photos/', blank=True, null=True, verbose_name="Photo de profil")
    date_inscription = models.DateTimeField(auto_now_add=True, verbose_name="Date d'inscription")

    class Meta:
        verbose_name = "Instructeur"
        verbose_name_plural = "Instructeurs"
        ordering = ['nom_complet']

    def __str__(self):
        return f"{self.nom_complet} ({self.email})"

    def nombre_cours_actifs(self):
        return self.courses.filter(statut='publié').count()

    def nombre_total_cours(self):
        return self.courses.count()

class Course(models.Model):
    STATUT_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('publié', 'Publié'),
        ('archivé', 'Archivé'),
    ]
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='brouillon', verbose_name="Statut")
    titre = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(verbose_name="Description", blank=True, null=True)
    instructeur = models.ForeignKey(Instructor, on_delete=models.CASCADE, verbose_name="Instructeur")
    prix = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix", validators=[MinValueValidator(0)])
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")

    class Meta:
        verbose_name = "Cours"
        verbose_name_plural = "Cours"
        ordering = ['titre']
        permissions = [
            ('can_publish_course', 'Peut publier un cours'),
            ('can_view_statistics', 'Peut voir les statistiques'),
        ]

    def __str__(self):
        return f"{self.titre} - {self.instructeur.nom_complet}"

    def nombre_inscriptions(self):
        return self.enrollments.count()

    def nombre_etudiants_actifs(self):
        return self.enrollments.filter(statut='en cours').count()

    def taux_completion(self):
        total = self.enrollments.count()
        if total == 0:
            return 0
        completes = self.enrollments.filter(statut='complété').count()
        return round((completes / total) * 100, 2)

    def est_disponible(self):
        return self.statut == 'publié'

class Enrollment(models.Model):
    STATUT_CHOICES = [
        ('en cours', 'En cours'),
        ('complété', 'Complété'),
        ('abandonné', 'Abandonné')
    ]

    cours = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="Cours", related_name="enrollments")
    étudiant = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Étudiant", related_name="enrollments")
    date_inscription = models.DateTimeField(auto_now_add=True, verbose_name="Date d'inscription")
    date_completion = models.DateTimeField(blank=True, null=True, verbose_name="Date de complétion")
    note_finale = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name="Note finale", validators=[MinValueValidator(0), MaxValueValidator(20)])
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='en cours', verbose_name="Statut")

    class Meta:
        verbose_name = "Inscription"
        verbose_name_plural = "Inscriptions"
        unique_together = [['cours', 'étudiant']]
        ordering = ['-date_inscription']

    def __str__(self):
        return f"{self.étudiant.username} - {self.cours.titre} ({self.statut})"

    def completer(self, note=None):
        self.statut = 'complété'
        self.date_completion = timezone.now()
        if note is not None:
            self.note_finale = note
        self.save()

    def abandonner(self):
        self.statut = 'abandonné'
        self.save()

    def duree_formation(self):
        if self.date_completion:
            return self.date_completion - self.date_inscription
        return None

    def est_reussi(self):
        if self.note_finale is not None:
            return self.note_finale >= 10
        return False

class StudentProfile(models.Model): 
    
    NIVEAU_CHOICES = [
        ('Licence', 'Licence'),
        ('Master', 'Master'),
        ('Doctorat', 'Doctorat'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile',
        verbose_name="Utilisateur"
    )
    
    numero_etudiant = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Numéro d'étudiant",
        help_text="Numéro unique d'identification de l'étudiant"
    )
    
    date_naissance = models.DateField(
        verbose_name="Date de naissance"
    )
    
    niveau_etudes = models.CharField(
        max_length=10,
        choices=NIVEAU_CHOICES,
        verbose_name="Niveau d'études"
    )
    
    class Meta:
        verbose_name = "Profil étudiant"
        verbose_name_plural = "Profils étudiants"
        ordering = ['numero_etudiant']
    
    def __str__(self):
        return f"{self.user.username} - {self.numero_etudiant} ({self.niveau_etudes})"
    
    def age(self):
        today = timezone.now().date()
        return today.year - self.date_naissance.year - (
            (today.month, today.day) < (self.date_naissance.month, self.date_naissance.day)
        )