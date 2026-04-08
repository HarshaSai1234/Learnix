from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from loginapp.models import User
from .models import Admin
from django.contrib.auth.hashers import make_password, check_password
from instructorapp.models import Teacher
from instructorapp.views import generate_username, generate_password

# Create your views here.

def adminhomepage(request):
    # Check if admin is logged in
    if not request.session.get('is_admin'):
        return redirect('loginpage')
    
    # Get all students from database
    students = User.objects.all().order_by('-id')
    
    # Get all admins from database
    admins = Admin.objects.all().order_by('-id')
    
    # Get pending teachers
    pending_teachers = Teacher.objects.filter(status='pending').order_by('-applied_at')
    
    # Get all teachers
    all_teachers = Teacher.objects.all().order_by('-applied_at')
    
    context = {
        'students': students,
        'total_students': students.count(),
        'admins': admins,
        'total_admins': admins.count(),
        'pending_teachers': pending_teachers,
        'total_pending_teachers': pending_teachers.count(),
        'all_teachers': all_teachers,
        'total_teachers': all_teachers.count()
    }
    return render(request, 'adminapp/adminhomepage.html', context)

def delete_student(request, student_id):
    # Check if admin is logged in
    if not request.session.get('is_admin'):
        return redirect('loginpage')
    
    if request.method == 'POST':
        try:
            student = User.objects.get(id=student_id)
            student_name = student.username
            student.delete()
            messages.success(request, f'Student {student_name} has been deleted successfully!')
        except User.DoesNotExist:
            messages.error(request, 'Student not found!')
    
    return redirect('adminhomepage')

def create_admin(request):
    # Check if admin is logged in
    if not request.session.get('is_admin'):
        return redirect('loginpage')
    
    if request.method == 'POST':
        username = request.POST.get('username', '')
        email = request.POST.get('email', '')
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        
        # Check if username already exists
        if Admin.objects.filter(username=username).exists():
            messages.error(request, 'Admin username is taken! Please choose another one.')
            return redirect('adminhomepage')
        
        # Check if email already exists
        if Admin.objects.filter(email=email).exists():
            messages.error(request, 'Email is already registered!')
            return redirect('adminhomepage')
        
        # Validate passwords match
        if password1 != password2:
            messages.error(request, 'Passwords do not match!')
            return redirect('adminhomepage')
        
        # Validate password length
        if len(password1) < 6:
            messages.error(request, 'Password must be at least 6 characters long!')
            return redirect('adminhomepage')
        
        # Create new admin
        try:
            admin = Admin.objects.create(
                username=username,
                email=email,
                password=make_password(password1)
            )
            messages.success(request, f'Admin account {username} created successfully!')
            return redirect('adminhomepage')
        except Exception as e:
            messages.error(request, f'Error creating admin account: {str(e)}')
            return redirect('adminhomepage')
    
    return redirect('adminhomepage')

def delete_admin(request, admin_id):
    # Check if admin is logged in
    if not request.session.get('is_admin'):
        return redirect('loginpage')
    
    # Check if trying to delete own account
    if request.session.get('admin_id') == admin_id:
        messages.error(request, 'You cannot delete your own admin account!')
        return redirect('adminhomepage')
    
    if request.method == 'POST':
        try:
            admin = Admin.objects.get(id=admin_id)
            admin_name = admin.username
            admin.delete()
            messages.success(request, f'Admin {admin_name} has been deleted successfully!')
        except Admin.DoesNotExist:
            messages.error(request, 'Admin not found!')
    
    return redirect('adminhomepage')

def approve_teacher(request, teacher_id):
    # Check if admin is logged in
    if not request.session.get('is_admin'):
        return redirect('loginpage')
    
    if request.method == 'POST':
        try:
            teacher = Teacher.objects.get(id=teacher_id)
            
            # Set username as full name and password as phone number
            username = teacher.full_name
            password = teacher.contact_number
            
            # Update teacher with credentials and approval
            teacher.username = username
            teacher.password = make_password(password)
            teacher.status = 'approved'
            teacher.approved_at = timezone.now()
            teacher.save()
            
            # Send email to teacher
            subject = 'Congratulations! Your Application Has Been Approved'
            message = f"""
Hello {teacher.full_name},

Congratulations! Your application to become a teacher at Learnix has been approved!

Here are your login credentials:
Username: {username}
Password: {password}

Please log in to your account at: {request.build_absolute_uri('/login/')}

Best regards,
Learnix Admin Team
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL or 'noreply@learnix.com',
                [teacher.email],
                fail_silently=False,
            )
            
            messages.success(request, f'Teacher {teacher.full_name} approved! Email sent with credentials.')
        except Teacher.DoesNotExist:
            messages.error(request, 'Teacher not found!')
        except Exception as e:
            messages.error(request, f'Error approving teacher: {str(e)}')
    
    return redirect('adminhomepage')

def reject_teacher(request, teacher_id):
    # Check if admin is logged in
    if not request.session.get('is_admin'):
        return redirect('loginpage')
    
    if request.method == 'POST':
        try:
            teacher = Teacher.objects.get(id=teacher_id)
            teacher_name = teacher.full_name
            teacher_email = teacher.email
            
            # Send rejection email
            subject = 'Application Status Update'
            message = f"""
Hello {teacher_name},

Thank you for your interest in becoming a teacher at Learnix. Unfortunately, your application has not been approved at this time.

We encourage you to try again or contact our support team for more information.

Best regards,
Learnix Admin Team
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL or 'noreply@learnix.com',
                [teacher_email],
                fail_silently=False,
            )
            
            teacher.status = 'rejected'
            teacher.save()
            
            messages.success(request, f'Teacher {teacher_name} rejected! Email sent.')
        except Teacher.DoesNotExist:
            messages.error(request, 'Teacher not found!')
        except Exception as e:
            messages.error(request, f'Error rejecting teacher: {str(e)}')
    
    return redirect('adminhomepage')

def delete_teacher(request, teacher_id):
    # Check if admin is logged in
    if not request.session.get('is_admin'):
        return redirect('loginpage')
    
    if request.method == 'POST':
        try:
            teacher = Teacher.objects.get(id=teacher_id)
            teacher_name = teacher.full_name
            teacher.delete()
            messages.success(request, f'Teacher {teacher_name} has been deleted successfully!')
        except Teacher.DoesNotExist:
            messages.error(request, 'Teacher not found!')
    
    return redirect('adminhomepage')
