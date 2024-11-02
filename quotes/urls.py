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
    path('element/<int:element_id>/materials/', views.manage_element_materials, name='manage_element_materials'),



    # Projects
    path('projects/', views.project_list, name='project_list'),
    path('projects/create/', views.project_create, name='project_create'),
    path('projects/edit/<int:project_id>/', views.edit_project, name='edit_project'),
    path('projects/delete/<int:project_id>/', views.project_delete, name='delete_project'),
    path('projects/<int:project_id>/edit/', views.project_list, name='project_edit'),
    path('projects/<int:project_id>/edit/', views.edit_project, name='edit_project'),
    path('projects/<int:project_id>/delete/', views.project_delete, name='project_delete'),
    path('projects/<int:project_id>/detail/', views.project_detail, name='project_detail'),
    path('project/<int:project_id>/edit/', views.edit_project, name='edit_project'),
    path('projects/edit/<int:project_id>/', views.edit_project, name='edit_project'),
    path('projects/<int:project_id>/admin-approve/', views.admin_approved_projects, name='admin_approve_project'),
    path('projects/<int:project_id>/customer-approve/', views.customer_approve_project, name='customer_approve_project'),
    path('projects/<int:project_id>/customer-decline/', views.customer_decline_project , name='customer_decline_project'),
    path('projects/<int:project_id>/mark-completed/', views.mark_project_completed, name='mark_project_completed'),
    path('project/<int:project_id>/complete/', views.mark_project_completed, name='mark_project_completed'),
    path('create-quotation/', views.create_quotation, name='create_quotation'),








    # Materials
    path('materials/', views.material_list, name='material_list'),
    path('materials/create/', views.material_create, name='material_create'),
    path('materials/delete/<int:material_id>/', views.material_delete, name='material_delete'),
    path('materials/<int:material_id>/edit/', views.material_edit, name='material_edit'),


    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/pending-projects/', views.admin_pending_projects, name='admin_pending_projects'),
    path('admin/declined-projects/', views.admin_declined_projects, name='admin_declined_projects'),
    path('admin/completed-projects/', views.admin_completed_projects, name='admin_completed_projects'),
    path('admin/user-management/', views.admin_user_management, name='admin_user_management'),
    path('admin/update-project-status/<int:project_id>/', views.update_project_status, name='update_project_status'),
    path('admin/approve-projects/', views.admin_approved_projects, name='admin_approved_projects'),
    path('admin/create-quotation/', views.admin_create_quotation, name='admin_create_quotation'),
    path('provide-quote/<int:project_id>/', views.provide_quote, name='provide_quote'),
    path('admin/delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('admin/project/<pk>/', views.admin_project_detail, name='admin_project_detail'),
    path('admin/projects/<int:project_id>/', views.admin_project_detail, name='admin_project_detail'),
    path('admin/project/<int:project_id>/', views.admin_project_detail, name='admin_project_detail'),


]