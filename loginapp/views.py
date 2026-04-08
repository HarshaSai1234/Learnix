from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from .models import User
from adminapp.models import Admin
from instructorapp.models import Teacher

# Create your views here.
def loginpage(request):
    if request.method == 'POST':
        login_input = request.POST.get('login_field', '')  # Can be email or username
        password = request.POST.get('password', '')
        
        # Check if login is for admin
        admin = None
        try:
            # Try to find admin by email first
            admin = Admin.objects.get(email=login_input)
        except Admin.DoesNotExist:
            try:
                # If not found by email, try by username
                admin = Admin.objects.get(username=login_input)
            except Admin.DoesNotExist:
                pass
        
        if admin and check_password(password, admin.password):
            # Store admin info in session
            request.session['is_admin'] = True
            request.session['admin_id'] = admin.id
            request.session['username'] = admin.username
            request.session['email'] = admin.email
            messages.success(request, f'Welcome back, Admin {admin.username}!')
            return redirect('adminhomepage')
        
        # If not admin, check if login is for student
        user = None
        try:
            # Try to find user by email first
            user = User.objects.get(email=login_input)
        except User.DoesNotExist:
            try:
                # If not found by email, try by username
                user = User.objects.get(username=login_input)
            except User.DoesNotExist:
                pass
        
        if user and check_password(password, user.password):
            # Store user info in session
            request.session['user_id'] = user.id
            request.session['username'] = user.username
            request.session['email'] = user.email
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('studenthomepage')
        
        # If not student, check if login is for teacher
        teacher = None
        try:
            # Try to find teacher by username (full name)
            teacher = Teacher.objects.get(username=login_input)
        except Teacher.DoesNotExist:
            try:
                # If not found by username, try by email
                teacher = Teacher.objects.get(email=login_input)
            except Teacher.DoesNotExist:
                pass
        
        if teacher and check_password(password, teacher.password):
            # Check if teacher is approved
            if teacher.status != 'approved':
                messages.error(request, 'Your application has not been approved yet. Please wait for admin approval.')
                return render(request, 'loginapp/loginpage.html')
            
            # Store teacher info in session
            request.session['is_teacher'] = True
            request.session['teacher_id'] = teacher.id
            request.session['username'] = teacher.username
            request.session['email'] = teacher.email
            messages.success(request, f'Welcome back, {teacher.full_name}!')
            return redirect('teacherhomepage')
        else:
            messages.error(request, 'Invalid username/email or password.')
        
        return render(request, 'loginapp/loginpage.html')
    return render(request,'loginapp/loginpage.html')

def registerpage(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        email = request.POST.get('email', '')
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is taken! Please choose another one.')
            return render(request, 'loginapp/registerpage.html')
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already registered! Please login or use a different email.')
            return render(request, 'loginapp/registerpage.html')

        # Validate passwords match
        if password1 != password2:
            messages.error(request, 'Passwords do not match!')
            return render(request, 'loginapp/registerpage.html')
        
        # Validate password length
        if len(password1) < 6:
            messages.error(request, 'Password must be at least 6 characters long!')
            return render(request, 'loginapp/registerpage.html')

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

def homepage(request):
    return render(request, 'loginapp/homepage.html')

def logout(request):
    # Clear all session data
    request.session.flush()
    messages.success(request, 'Logged out successfully!')
    return redirect('loginpage')

def teacherhomepage(request):
    # Check if teacher is logged in
    if not request.session.get('is_teacher'):
        return redirect('loginpage')
    
    # Get teacher data from session
    teacher_id = request.session.get('teacher_id')
    
    try:
        teacher = Teacher.objects.get(id=teacher_id)
        context = {
            'teacher': teacher,
            'full_name': teacher.full_name,
            'email': teacher.email,
            'username': teacher.username
        }
        return render(request, 'teacherapp/teacherhomepage.html', context)
    except Teacher.DoesNotExist:
        return redirect('loginpage')
