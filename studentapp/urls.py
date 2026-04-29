from django.urls import path
from . import views

urlpatterns = [
    path('', views.student_dashboard, name='studenthomepage'),
    path('assignments/', views.view_assignments, name='view_assignments'),
    path('submit/<int:assignment_id>/', views.submit_assignment, name='submit_assignment'),
    path('explore/', views.explore_courses, name='explore_courses'),
    path('enroll/<int:course_id>/', views.join_course, name='join_course'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('rate/<int:course_id>/', views.rate_teacher, name='rate_teacher'),
    path('progress/', views.view_progress, name='view_progress'),
]
