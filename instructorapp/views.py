from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from .models import Teacher, Course, Enrollment, Assignment, Submission
from loginapp.models import User
from django.utils import timezone
import string
import random

# --- TEACHER DASHBOARD ---
def teacher_dashboard(request):
    if not request.session.get('is_teacher'):
        return redirect('loginpage')
    
    teacher_id = request.session.get('teacher_id')
    try:
        teacher = Teacher.objects.get(id=teacher_id)
        courses = teacher.courses.all()
        total_students = User.objects.filter(role='student').count()
        assignments_count = Assignment.objects.filter(teacher=teacher).count()
        
        context = {
            'teacher': teacher,
            'full_name': teacher.full_name,
            'email': teacher.email,
            'username': teacher.username,
            'course_count': courses.count(),
            'total_students': total_students,
            'assignments_count': assignments_count,
            'courses': courses,
            'assignments': Assignment.objects.filter(teacher=teacher).order_by('-created_at')
        }
        return render(request, 'teacherapp/teacherhomepage.html', context)
    except Teacher.DoesNotExist:
        return redirect('logout')

# --- COURSE MANAGEMENT ---
def create_course(request):
    if not request.session.get('is_teacher'):
        return redirect('loginpage')
        
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        teacher = Teacher.objects.get(id=request.session.get('teacher_id'))
        
        Course.objects.create(teacher=teacher, title=title, description=description)
        messages.success(request, 'Course created successfully!')
        return redirect('teacher_dashboard')
        
    return render(request, 'teacherapp/create_course.html')

# --- STUDENT MANAGEMENT ---
def view_students(request):
    if not request.session.get('is_teacher'):
        return redirect('loginpage')
    
    students = User.objects.filter(role='student').order_by('-id')
    return render(request, 'teacherapp/view_students.html', {'students': students})

# --- ASSIGNMENT MANAGEMENT ---
def add_assignment(request):
    if not request.session.get('is_teacher'):
        return redirect('loginpage')
        
    teacher = Teacher.objects.get(id=request.session.get('teacher_id'))
    courses = teacher.courses.all()
    
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        title = request.POST.get('title')
        content = request.POST.get('content')
        due_date = request.POST.get('due_date')
        attachment = request.FILES.get('attachment')
        
        Assignment.objects.create(
            course_id=course_id,
            teacher=teacher,
            title=title,
            content=content,
            attachment=attachment,
            due_date=due_date
        )
        messages.success(request, 'Assignment posted successfully!')
        return redirect('teacher_dashboard')
        
    return render(request, 'teacherapp/add_assignment.html', {'courses': courses})

# --- GRADING SYSTEM ---
def view_submissions(request, assignment_id):
    if not request.session.get('is_teacher'):
        return redirect('loginpage')
        
    assignment = Assignment.objects.get(id=assignment_id)
    submissions = assignment.submissions.all().order_by('-submitted_at')
    
    if request.method == 'POST':
        # NEW: Check if deadline has passed
        if timezone.now() > assignment.due_date:
            messages.error(request, 'The deadline for this assignment has passed. Grades are now locked.')
            return redirect('view_submissions', assignment_id=assignment_id)
            
        submission_id = request.POST.get('submission_id')
        grade = request.POST.get('grade')
        feedback = request.POST.get('feedback')
        
        submission = Submission.objects.get(id=submission_id)
        submission.grade = grade
        submission.feedback = feedback
        submission.save()
        messages.success(request, f'Grade updated for student {submission.student_name}')
        return redirect('view_submissions', assignment_id=assignment_id)
        
    return render(request, 'teacherapp/view_submissions.html', {
        'assignment': assignment,
        'submissions': submissions,
        'deadline_passed': timezone.now() > assignment.due_date
    })

# --- STUDENT ACTIONS ---
def join_course(request, course_id):
    if not request.session.get('user_id') or request.session.get('role') != 'student':
        return redirect('loginpage')
        
    username = request.session.get('username')
    course = Course.objects.get(id=course_id)
    
    # Check if already enrolled
    if not Enrollment.objects.filter(student_name=username, course=course).exists():
        Enrollment.objects.create(student_name=username, course=course)
        messages.success(request, f'You have successfully joined "{course.title}"!')
    else:
        messages.info(request, 'You are already enrolled in this course.')
        
    return redirect('studenthomepage')

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
            messages.success(request, 'Application submitted successfully! Our team will review it shortly. You will receive an email once approved.')
            return redirect('teacher_register')
        except Exception as e:
            messages.error(request, f'Error submitting application: {str(e)}')
            return render(request, 'instructorapp/teacher_register.html')
    
    return render(request, 'instructorapp/teacher_register.html')

def manage_course(request, course_id):
    if not request.session.get('is_teacher'):
        return redirect('loginpage')
    
    teacher = Teacher.objects.get(id=request.session.get('teacher_id'))
    course = Course.objects.get(id=course_id, teacher=teacher)
    
    if request.method == 'POST':
        if 'delete' in request.POST:
            course.delete()
            messages.success(request, f'Course "{course.title}" deleted successfully.')
            return redirect('teacher_dashboard')
        
        course.title = request.POST.get('title')
        course.description = request.POST.get('description')
        course.save()
        messages.success(request, 'Course updated successfully!')
        return redirect('teacher_dashboard')
        
    return render(request, 'teacherapp/edit_course.html', {'course': course})

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
