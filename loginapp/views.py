from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from .models import User

# Create your views here.
def loginpage(request):
    if request.method == 'POST':
        return redirect('studenthomepage')
    return render(request,'loginapp/loginpage.html')

def registerpage(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        email = request.POST.get('email', '')
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        # Create new user
        try:
            user = User.objects.create(
                username=username,
                email=email,
                password=make_password(password1)
            )
            messages.success(request, 'Account created successfully! Please login.')
            return redirect('loginpage')
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return render(request, 'loginapp/registerpage.html')
    
    return render(request, 'loginapp/registerpage.html')

def studenthomepage(request):
    return render(request, 'studentapp/studenthomepage.html')
