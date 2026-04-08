from django.db import models

# Create your models here.
class Teacher(models.Model):
    APPROVAL_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    address = models.TextField()
    contact_number = models.CharField(max_length=15)
    resume = models.FileField(upload_to='resumes/')
    username = models.CharField(max_length=100, blank=True, null=True, unique=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=APPROVAL_CHOICES, default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return self.full_name
    
    class Meta:
        db_table = 'teachers'