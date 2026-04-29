from django.urls import path
from . import views

urlpatterns = [
    path('', views.student_dashboard, name='studenthomepage'),
    path('assignments/', views.view_assignments, name='view_assignments'),
    path('submit/<int:assignment_id>/', views.submit_assignment, name='submit_assignment'),
    path('explore/', views.explore_courses, name='explore_courses'),
    path('progress/', views.view_progress, name='view_progress'),
]
