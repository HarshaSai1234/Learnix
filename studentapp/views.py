from django.shortcuts import render, redirect
from django.contrib import messages
from instructorapp.models import Enrollment, Assignment, Course, Submission
from loginapp.models import User

# --- STUDENT DASHBOARD ---
def student_dashboard(request):
    if not request.session.get('user_id') or request.session.get('role') != 'student':
        return redirect('loginpage')
    
    username = request.session.get('username')
    enrollments = Enrollment.objects.filter(student_name=username)
    enrolled_course_ids = enrollments.values_list('course_id', flat=True)
    
    all_assignments = Assignment.objects.filter(course_id__in=enrolled_course_ids).order_by('due_date')
    
    pending_assignments = []
    completed_assignments = []
    
    for assignment in all_assignments:
        submission = Submission.objects.filter(assignment=assignment, student_name=username).first()
        if submission:
            assignment.submission = submission
            completed_assignments.append(assignment)
        else:
            pending_assignments.append(assignment)
    
    context = {
        'course_count': enrollments.count(),
        'enrolled_courses': Course.objects.filter(id__in=enrolled_course_ids),
        'pending_assignments': pending_assignments,
        'completed_assignments': completed_assignments,
        'assignments_count': len(pending_assignments), # Show pending count in stats
    }
    return render(request, 'studentapp/studenthomepage.html', context)

# --- VIEW ASSIGNMENTS ---
def view_assignments(request):
    if not request.session.get('user_id') or request.session.get('role') != 'student':
        return redirect('loginpage')
        
    username = request.session.get('username')
    enrolled_course_ids = Enrollment.objects.filter(student_name=username).values_list('course_id', flat=True)
    assignments = Assignment.objects.filter(course_id__in=enrolled_course_ids).order_by('-due_date')
    
    # Map assignments to existing submissions for this student
    # We'll attach the submission object directly to each assignment for the template
    for assignment in assignments:
        assignment.user_submission = Submission.objects.filter(assignment=assignment, student_name=username).first()
    
    return render(request, 'studentapp/view_assignments.html', {'assignments': assignments})

# --- EXPLORE COURSES ---
def explore_courses(request):
    if not request.session.get('user_id') or request.session.get('role') != 'student':
        return redirect('loginpage')
        
    username = request.session.get('username')
    enrolled_course_ids = Enrollment.objects.filter(student_name=username).values_list('course_id', flat=True)
    courses = Course.objects.exclude(id__in=enrolled_course_ids)
    
    return render(request, 'studentapp/explore_courses.html', {'courses': courses})

# --- SUBMIT ASSIGNMENT ---
def submit_assignment(request, assignment_id):
    if not request.session.get('user_id') or request.session.get('role') != 'student':
        return redirect('loginpage')
        
    if request.method == 'POST':
        username = request.session.get('username')
        submission_file = request.FILES.get('submission_file')
        
        if submission_file:
            # Safer Handle Re-submission (Edit)
            submission = Submission.objects.filter(
                assignment_id=assignment_id,
                student_name=username
            ).first()
            
            if not submission:
                submission = Submission.objects.create(
                    assignment_id=assignment_id,
                    student_name=username,
                    submission_file=submission_file
                )
                messages.success(request, 'Assignment submitted successfully!')
            else:
                # NEW: Block editing if already graded
                if submission.grade:
                    messages.error(request, 'This assignment has already been graded and cannot be edited.')
                else:
                    submission.submission_file = submission_file
                    submission.save()
                    messages.success(request, 'Submission updated successfully!')
        else:
            messages.error(request, 'Please select a file to upload.')
            
    return redirect('view_assignments')

# --- MY PROGRESS ---
def view_progress(request):
    if not request.session.get('user_id') or request.session.get('role') != 'student':
        return redirect('loginpage')
        
    username = request.session.get('username')
    enrollments = Enrollment.objects.filter(student_name=username)
    
    return render(request, 'studentapp/view_progress.html', {'enrollments': enrollments})
