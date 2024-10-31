from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Project, Material, Pricing
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import ProjectForm

@login_required
def project_list(request):
    projects = Project.objects.filter(user=request.user)
    return render(request, 'quotes/project_list.html', {'projects': projects})

@login_required
def project_create(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST.get('description', '')
        project = Project(user=request.user, title=title, description=description)
        project.save()
        return redirect('project_list')
    return render(request, 'quotes/project_create.html')

@login_required
def project_delete(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    if request.method == 'POST':
        project.delete()
        return redirect('project_list')
    return render(request, 'quotes/project_delete.html', {'project': project})

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
        return redirect('material_list')
    return render(request, 'quotes/material_create.html')

@login_required
def material_delete(request, material_id):
    material = get_object_or_404(Material, id=material_id)
    if request.method == 'POST':
        material.delete()
        return redirect('material_list')
    return render(request, 'quotes/material_delete.html', {'material': material})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('project_list')
    else:
        form = UserCreationForm()
    return render(request, 'quotes/register.html', {'form': form})

def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project created successfully!')
            return redirect('project_list')
    else:
        form = ProjectForm()
    return render(request, 'project_form.html', {'form': form})

def edit_project(request, project_id):
    project = Project.objects.get(id=project_id, user=request.user)  # Ensure the user owns the project
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully!')
            return redirect('project_list')
    else:
        form = ProjectForm(instance=project)
    return render(request, 'quotes/project_form.html', {'form': form})

def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)  # Ensure the user owns the project
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project deleted successfully!')
        return redirect('project_list')
    return render(request, 'quotes/confirm_delete.html', {'project': project})

def request_quote(request):
    if request.method == "POST":
        # Get form data from the POST request
        # ...

        # Create a new QuoteRequest object and assign the logged-in user
        quote_request = QuoteRequest(
            # ...other fields...
            user=request.user
        )
        quote_request.save()

        return redirect("success_page")
    else:
        # Render the form
        return render(request, "request_quote.html")