from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .models import Project, Material, Pricing
from .forms import CustomUserCreationForm
from django.contrib.auth import logout
from django.http import HttpResponseNotAllowed


def home(request):
    return render(request, 'quotes/home.html')


@login_required
def project_list(request):
    projects = Project.objects.filter(user=request.user).order_by('-created_at')  # Add ordering if desired
    context = {
        'projects': projects
    }
    return render(request, 'quotes/project_list.html', context)

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')  # Redirect to your login page
    else:
        return HttpResponseNotAllowed(['POST'])


@login_required
def project_create(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST.get('description', '')
        project = Project(user=request.user, title=title, description=description)
        project.save()
        messages.success(request, 'Project created successfully!')
        return redirect('project_list')
    return render(request, 'quotes/project_create.html')


@login_required
def project_delete(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project deleted successfully!')
        return redirect('project_list')
    return render(request, 'quotes/project_delete.html', {'project': project})


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
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            messages.success(request, 'Project created successfully!')
            return redirect('project_list')
    else:
        form = ProjectForm()
    return render(request, 'quotes/project_form.html', {'form': form})


@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully!')
            return redirect('project_list')
    else:
        form = ProjectForm(instance=project)
    return render(request, 'quotes/project_form.html', {'form': form})


@login_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project deleted successfully!')
        return redirect('project_list')
    return render(request, 'quotes/confirm_delete.html', {'project': project})


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