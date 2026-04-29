from django.urls import path
from . import views

urlpatterns = [
    path('', views.teacher_dashboard, name='teacher_dashboard'),
    path('register/', views.teacher_register, name='teacher_register'),
    path('create-course/', views.create_course, name='create_course'),
    path('students/', views.view_students, name='view_students'),
    path('add-assignment/', views.add_assignment, name='add_assignment'),
    path('view-submissions/<int:assignment_id>/', views.view_submissions, name='view_submissions'),
    path('download-submission/<int:submission_id>/', views.download_submission, name='download_submission'),
    path('grade-submission/<int:submission_id>/', views.grade_submission, name='grade_submission'),
    path('manage-course/<int:course_id>/', views.manage_course, name='manage_course'),
    path('join-course/<int:course_id>/', views.join_course, name='join_course'),
]
