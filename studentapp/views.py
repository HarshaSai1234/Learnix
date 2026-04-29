from django.shortcuts import render, redirect
from django.contrib import messages
from instructorapp.models import Enrollment, Assignment, Course, Submission, Rating
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
    # Only show courses from approved teachers that student is not enrolled in
    courses = Course.objects.filter(teacher__status='approved').exclude(id__in=enrolled_course_ids)
    
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

# --- ENROLL IN COURSE ---
def join_course(request, course_id):
    if not request.session.get('user_id') or request.session.get('role') != 'student':
        return redirect('loginpage')
    
    try:
        course = Course.objects.get(id=course_id)
        username = request.session.get('username')
        
        # Check if already enrolled
        if Enrollment.objects.filter(course=course, student_name=username).exists():
            messages.warning(request, 'You are already enrolled in this course.')
        else:
            # Create enrollment
            Enrollment.objects.create(course=course, student_name=username)
            messages.success(request, f'Successfully enrolled in {course.title}!')
    except Course.DoesNotExist:
        messages.error(request, 'Course not found.')
    
    return redirect('explore_courses')

# --- MY PROGRESS ---
def view_progress(request):
    if not request.session.get('user_id') or request.session.get('role') != 'student':
        return redirect('loginpage')
        
    username = request.session.get('username')
    enrollments = Enrollment.objects.filter(student_name=username)
    
    return render(request, 'studentapp/view_progress.html', {'enrollments': enrollments})

# --- VIEW COURSE DETAIL ---
def course_detail(request, course_id):
    if not request.session.get('user_id') or request.session.get('role') != 'student':
        return redirect('loginpage')
    
    try:
        course = Course.objects.get(id=course_id)
        username = request.session.get('username')
        
        # Check if student is enrolled
        if not Enrollment.objects.filter(course=course, student_name=username).exists():
            messages.error(request, 'You are not enrolled in this course.')
            return redirect('explore_courses')
        
        # Get assignments for this course
        assignments = course.assignments.all().order_by('-due_date')
        
        # Get average rating
        average_rating = course.get_average_rating()
        
        # Check if student has already rated
        existing_rating = Rating.objects.filter(teacher=course.teacher, student_name=username, course=course).first()
        
        context = {
            'course': course,
            'assignments': assignments,
            'average_rating': average_rating,
            'existing_rating': existing_rating,
            'teacher': course.teacher,
        }
        return render(request, 'studentapp/course_detail.html', context)
    except Course.DoesNotExist:
        messages.error(request, 'Course not found.')
        return redirect('explore_courses')

# --- RATE TEACHER ---
def rate_teacher(request, course_id):
    if not request.session.get('user_id') or request.session.get('role') != 'student':
        return redirect('loginpage')
    
    if request.method == 'POST':
        try:
            course = Course.objects.get(id=course_id)
            username = request.session.get('username')
            rating_value = request.POST.get('rating')
            feedback = request.POST.get('feedback', '')
            
            # Validate rating
            if not rating_value or int(rating_value) < 1 or int(rating_value) > 5:
                messages.error(request, 'Invalid rating. Please select between 1-5 stars.')
                return redirect('course_detail', course_id=course_id)
            
            # Check if already rated
            existing_rating = Rating.objects.filter(teacher=course.teacher, student_name=username, course=course).first()
            
            if existing_rating:
                # Update rating
                existing_rating.rating = int(rating_value)
                existing_rating.feedback = feedback
                existing_rating.save()
                messages.success(request, 'Rating updated successfully!')
            else:
                # Create new rating
                Rating.objects.create(
                    teacher=course.teacher,
                    student_name=username,
                    course=course,
                    rating=int(rating_value),
                    feedback=feedback
                )
                messages.success(request, 'Thank you for rating!')
        except Course.DoesNotExist:
            messages.error(request, 'Course not found.')
        except Exception as e:
            messages.error(request, f'Error submitting rating: {str(e)}')
    
    return redirect('course_detail', course_id=course_id)
