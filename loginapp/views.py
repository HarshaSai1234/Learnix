from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from .models import User
from adminapp.models import Admin
from instructorapp.models import Teacher
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(request, *args, **kwargs):
        if 'role' not in request.session:
            messages.error(request, 'Please login first!')
            return redirect('loginpage')
        return f(request, *args, **kwargs)
    return decorated_function

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
            request.session['role'] = 'admin'
            request.session['admin_id'] = admin.id
            request.session['username'] = admin.username
            request.session['email'] = admin.email
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
            request.session['role'] = 'student'
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
            request.session['role'] = 'teacher'
            request.session['teacher_id'] = teacher.id
            request.session['username'] = teacher.username
            request.session['email'] = teacher.email
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
                password=make_password(password1),
                role='student'
            )
            messages.success(request, 'Account created successfully! Please login.')
            return redirect('loginpage')
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return render(request, 'loginapp/registerpage.html')
    
    return render(request, 'loginapp/registerpage.html')

def studenthomepage(request):
    return redirect('studenthomepage')

def homepage(request):
    role = request.session.get('role')
    if role == 'student':
        return redirect('studenthomepage')
    elif role == 'teacher':
        return redirect('teacherhomepage')
    elif role == 'admin':
        return redirect('adminhomepage')
    return render(request, 'loginapp/homepage.html')

def logout(request):
    # Clear all session data
    request.session.flush()
    messages.success(request, 'Logged out successfully!')
    return redirect('loginpage')

def teacherhomepage(request):
    return redirect('teacher_dashboard')

def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password', '')
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        role = request.session.get('role')
        user_obj = None
        
        # Identify the user object based on role
        if role == 'admin':
            user_obj = Admin.objects.get(id=request.session['admin_id'])
        elif role == 'teacher':
            user_obj = Teacher.objects.get(id=request.session['teacher_id'])
        elif role == 'student':
            user_obj = User.objects.get(id=request.session['user_id'])
            
        if not user_obj:
            messages.error(request, 'User not found.')
            return redirect('loginpage')
            
        # Verify current password
        if not check_password(current_password, user_obj.password):
            messages.error(request, 'Current password is incorrect.')
            return render(request, 'loginapp/change_password.html')
            
        # Verify new passwords match
        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
            return render(request, 'loginapp/change_password.html')
            
        # Validate password length
        if len(new_password) < 6:
            messages.error(request, 'Password must be at least 6 characters long.')
            return render(request, 'loginapp/change_password.html')
            
        # Update password
        user_obj.password = make_password(new_password)
        user_obj.save()
        
        messages.success(request, 'Password changed successfully!')
        
        # Redirect based on role
        if role == 'admin':
            return redirect('adminhomepage')
        elif role == 'teacher':
            return redirect('teacherhomepage')
        else:
            return redirect('studenthomepage')
            
    return render(request, 'loginapp/change_password.html')

def profile(request):
    role = request.session.get('role')
    user_data = {
        'username': request.session.get('username'),
        'email': request.session.get('email'),
        'role': role.capitalize()
    }
    
    # Add full name if available (specifically for teachers)
    if role == 'teacher':
        try:
            teacher = Teacher.objects.get(id=request.session['teacher_id'])
            user_data['full_name'] = teacher.full_name
        except:
            pass
    elif role == 'student':
        user_data['full_name'] = request.session.get('username') # Students use username as name currently
        
    return render(request, 'loginapp/profile.html', {'user': user_data})
