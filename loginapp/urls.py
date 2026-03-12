from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('login/', views.loginpage, name='loginpage'),
    path('register/', views.registerpage, name='registerpage'),
    path('student-dashboard/', views.studenthomepage, name='studenthomepage'),
]