from django.db import models
from django.contrib.auth.hashers import make_password

# Create your models here.

class Admin(models.Model):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.username
    
    class Meta:
        db_table = 'admins'
