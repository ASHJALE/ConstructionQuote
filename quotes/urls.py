from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import logout_view

urlpatterns = [
    # Home
    path('', views.home, name='home'),  # Keep only one home URL

    # Authentication
    path('login/', views.login_view, name='login'),  # Use your custom login view
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('logout/', logout_view, name='logout'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # Projects
    path('projects/', views.project_list, name='project_list'),
    path('projects/create/', views.project_create, name='project_create'),
    path('projects/edit/<int:project_id>/', views.edit_project, name='edit_project'),
    path('projects/delete/<int:project_id>/', views.delete_project, name='delete_project'),


    # Materials
    path('materials/', views.material_list, name='material_list'),
    path('materials/create/', views.material_create, name='material_create'),
    path('materials/delete/<int:material_id>/', views.material_delete, name='material_delete'),
]