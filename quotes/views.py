from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.http import require_http_methods
from django.contrib.admin.views.decorators import staff_member_required
from .models import Project, Material, Pricing
from .forms import CustomUserCreationForm, ProjectForm
from django.contrib.auth import logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .models import Project


def home(request):
    return render(request, 'quotes/home.html')


@login_required
def project_list(request):
    projects = Project.objects.filter(user=request.user).order_by('-created_at')  # Add ordering if desired
    context = {
        'projects': projects
    }
    return render(request, 'quotes/project_list.html', context)



@require_http_methods(["POST"])
def logout_view(request):
    logout(request)
    return redirect('project_list')

@login_required
def project_create(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST.get('description', '')
        project_type = request.POST.get('project_type')
        area_size = request.POST.get('area_size')
        project_element = request.POST.get('project_element')

        project = Project(
            user=request.user,
            title=title,
            description=description,
            project_type=project_type,
            area_size=area_size,
            project_element=project_element
        )
        project.save()
        messages.success(request, 'Project created successfully!')
        return redirect('project_list')
    return render(request, 'quotes/project_form.html')


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('project_list')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()

    # Add classes to form fields
    for field in form.fields.values():
        field.widget.attrs['class'] = 'form-control'

    return render(request, 'quotes/login.html', {'form': form})


@login_required
def material_list(request):
    materials = Material.objects.all()
    return render(request, 'quotes/material_list.html', {'materials': materials})


@login_required
def material_create(request):
    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST.get('description', '')
        unit_price = request.POST['unit_price']
        material = Material(name=name, description=description, unit_price=unit_price)
        material.save()
        messages.success(request, 'Material created successfully!')
        return redirect('material_list')
    return render(request, 'quotes/material_create.html')


@login_required
def material_delete(request, material_id):
    material = get_object_or_404(Material, id=material_id)
    if request.method == 'POST':
        material.delete()
        messages.success(request, 'Material deleted successfully!')
        return redirect('material_list')
    return render(request, 'quotes/material_delete.html', {'material': material})


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to our platform.')
            return redirect('project_list')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = CustomUserCreationForm()
    return render(request, 'quotes/register.html', {'form': form})


@login_required
def project_create(request):
    if request.method == 'POST':
        try:
            # Get form data
            project = Project(
                user=request.user,
                title=request.POST['title'],
                description=request.POST.get('description', ''),
                project_type=request.POST['project_type'],
                area_size=request.POST['area_size'],
                project_element=request.POST['project_element']  # Make sure this matches your form field name
            )
            project.save()
            messages.success(request, 'Project created successfully!')
            return redirect('project_list')
        except Exception as e:
            messages.error(request, f'Error creating project: {str(e)}')
            print(f"Form data: {request.POST}")  # Debug print

    # Get choices for the template
    context = {
        'project_types': Project.PROJECT_TYPES,
        'project_elements': Project.PROJECT_ELEMENTS,
    }
    return render(request, 'quotes/project_form.html', context)


@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)

    if request.method == 'POST':
        # Get form data
        title = request.POST.get('title')
        description = request.POST.get('description')
        project_type = request.POST.get('project_type')
        area_size = request.POST.get('area_size')
        project_element = request.POST.get('project_elements')

        # Update project
        project.title = title
        project.description = description
        project.project_type = project_type
        project.area_size = area_size
        project.project_element = project_element
        project.save()

        messages.success(request, 'Project updated successfully!')
        return redirect('project_list')

    return render(request, 'quotes/project_edit.html', {'project': project})


@login_required
def request_quote(request):
    if request.method == "POST":
        # Get form data from the POST request
        # ... (You'll need to add the form processing logic here)

        # Create a new QuoteRequest object and assign the logged-in user
        quote_request = QuoteRequest(
            # ...other fields...
            user=request.user
        )
        quote_request.save()
        messages.success(request, 'Quote request submitted successfully!')
        return redirect("success_page")
    else:
        # Render the form
        return render(request, "quotes/request_quote.html")

@staff_member_required
def admin_dashboard(request):
    projects_list = Project.objects.all().order_by('-created_at')
    users_list = User.objects.all()

    # Pagination for projects
    project_paginator = Paginator(projects_list, 10)  # Show 10 projects per page
    project_page = request.GET.get('project_page')
    projects = project_paginator.get_page(project_page)

    # Pagination for users
    user_paginator = Paginator(users_list, 10)  # Show 10 users per page
    user_page = request.GET.get('user_page')
    users = user_paginator.get_page(user_page)

    context = {
        'projects': projects,
        'users': users,
    }
    return render(request, 'quotes/admin_dashboard.html', context)


def delete_user(request, user_id):
    user_to_delete = get_object_or_404(User, id=user_id)

    # Prevent deletion of superusers and self-deletion
    if user_to_delete.is_superuser or user_to_delete == request.user:
        messages.error(request, "Cannot delete this user.")
        return redirect('admin_dashboard')

    if request.method == 'POST':
        # Delete the user's projects first
        Project.objects.filter(user=user_to_delete).delete()
        # Then delete the user
        user_to_delete.delete()
        messages.success(request, f"User {user_to_delete.username} and all their projects have been deleted.")
        return redirect('admin_dashboard')

    return render(request, 'quotes/confirm_user_delete.html', {'user_to_delete': user_to_delete})


def project_delete(request, project_id):
    # For admin users, don't filter by user
    if request.user.is_staff:
        project = get_object_or_404(Project, id=project_id)
    else:
        # For regular users, filter by user
        project = get_object_or_404(Project, id=project_id, user=request.user)

    if request.method == 'POST':
        project_title = project.title
        project.delete()
        messages.success(request, f'Project "{project_title}" has been deleted successfully.')

        # Redirect based on user type
        if request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('project_list')

    return render(request, 'quotes/project_delete.html', {'project': project})

def project_edit(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully!')
            return redirect('project_list')
    else:
        form = ProjectForm(instance=project)
    return render(request, 'quotes/project_form.html', {'form': form, 'project': project})

def is_admin(user):
    return user.is_superuser