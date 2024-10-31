from django.urls import path
from . import views
from .views import register
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('projects/', views.project_list, name='project_list'),
    path('projects/create/', views.project_create, name='project_create'),
    path('projects/delete/<int:project_id>/', views.project_delete, name='project_delete'),
    path('materials/', views.material_list, name='material_list'),
    path('materials/create/', views.material_create, name='material_create'),
    path('materials/delete/<int:material_id>/', views.material_delete, name='material_delete'),
    path('register/', register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='quotes/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('projects/edit/<int:project_id>/', views.edit_project, name='edit_project'),
    path('projects/delete/<int:project_id>/', views.delete_project, name='delete_project'),


]