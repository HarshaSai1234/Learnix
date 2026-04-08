from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.adminhomepage, name='adminhomepage'),
    path('delete-student/<int:student_id>/', views.delete_student, name='delete_student'),
    path('create-admin/', views.create_admin, name='create_admin'),
    path('delete-admin/<int:admin_id>/', views.delete_admin, name='delete_admin'),
    path('approve-teacher/<int:teacher_id>/', views.approve_teacher, name='approve_teacher'),
    path('reject-teacher/<int:teacher_id>/', views.reject_teacher, name='reject_teacher'),
    path('delete-teacher/<int:teacher_id>/', views.delete_teacher, name='delete_teacher'),
]
