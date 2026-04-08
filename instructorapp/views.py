from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password
from .models import Teacher
import string
import random

# Create your views here.

def teacher_register(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address', '')
        contact_number = request.POST.get('contact_number', '')
        resume = request.FILES.get('resume', None)
        
        # Validation
        if not all([full_name, email, address, contact_number, resume]):
            messages.error(request, 'All fields are required!')
            return render(request, 'instructorapp/teacher_register.html')
        
        # Check if email already exists
        if Teacher.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered!')
            return render(request, 'instructorapp/teacher_register.html')
        
        # Create teacher application
        try:
            teacher = Teacher.objects.create(
                full_name=full_name,
                email=email,
                address=address,
                contact_number=contact_number,
                resume=resume,
                status='pending'
            )
            messages.success(request, 'Application submitted successfully! Please wait for admin approval.')
            return redirect('teacher_register')
        except Exception as e:
            messages.error(request, f'Error submitting application: {str(e)}')
            return render(request, 'instructorapp/teacher_register.html')
    
    return render(request, 'instructorapp/teacher_register.html')

def generate_username(full_name):
    """Generate username from full name"""
    base_username = full_name.lower().replace(' ', '_')[:20]
    username = base_username
    counter = 1
    while Teacher.objects.filter(username=username).exists():
        username = f"{base_username}_{counter}"
        counter += 1
    return username

def generate_password(length=10):
    """Generate random password"""
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))
