from django.urls import path
from . import views

urlpatterns = [
    # Home
    path('', views.home, name='home'),

    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),  # Use your custom logout view
    path('register/', views.register, name='register'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/delete-user/<int:user_id>/', views.delete_user, name='delete_user'),


    # Projects
    path('projects/', views.project_list, name='project_list'),
    path('projects/create/', views.project_create, name='project_create'),
    path('projects/edit/<int:project_id>/', views.edit_project, name='edit_project'),
    path('projects/delete/<int:project_id>/', views.project_delete, name='delete_project'),
    path('projects/<int:project_id>/edit/', views.project_edit, name='project_edit'),
    path('projects/<int:project_id>/delete/', views.project_delete, name='project_delete'),

    # Materials
    path('materials/', views.material_list, name='material_list'),
    path('materials/create/', views.material_create, name='material_create'),
    path('materials/delete/<int:material_id>/', views.material_delete, name='material_delete'),
]