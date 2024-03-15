"""
URL configuration for TASK_PROJECT project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# urls.py

from django.urls import path
from task_app import views
from django.contrib.auth import views as auth_views
from .views import CustomPasswordResetView  # Import your CustomPasswordResetView


urlpatterns = [

    path('', views.Signup, name='signup'),
    path("login/", views.loginuser, name='login'),
    path("index/", views.index, name='index'),
    path("logout/", views.logoutuser, name='logout'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('verify_login/', views.verify_otp, name='verify_login'),
    path("password_reset/", CustomPasswordResetView.as_view(), name='forget_password'),
    path("password_reset_done/", auth_views.PasswordChangeDoneView.as_view(template_name='auth/pass_reset_done.html')  , name='password_reset_done'),
    path("password_reset_confirm/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path("password_reset_complete/", auth_views.PasswordResetCompleteView.as_view(template_name='auth/pass_reset_complete.html')  , name='password_reset_complete'),

    path("addtask/",views.add_task, name='add_task'),
    path("delete_todo/<int:todo_id>/",views.delete_todo, name='delete_todo'),
    path("change-status/<int:todo_id>/<str:status>",views.change_todo, name='change_todo'),
    path('edit_todo/<int:todo_id>/', views.edit_todo, name='edit_todo'),
    path("chart/",views.chart, name='chart'),
    
    

]








