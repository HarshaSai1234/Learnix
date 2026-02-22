from django.urls import path
from . import views

urlpatterns = [
    path('', views.loginpage, name='loginpage'),
    path('register/', views.registerpage, name='registerpage'),
    path('student-dashboard/', views.studenthomepage, name='studenthomepage'),
]