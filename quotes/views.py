
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .admin import ElementMaterialForm
from .models import Project, Material, Pricing, ProjectElement, ElementMaterial
from .forms import CustomUserCreationForm, ProjectForm
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Project, User

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
        try:
            # Get form data
            project = Project(
                user=request.user,
                title=request.POST['title'],
                description=request.POST.get('description', ''),
                location=request.POST.get('location', ''),  # Add this line
                project_type=request.POST['project_type'],
                area_size=request.POST['area_size'],
                project_element=request.POST['project_element']
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
    materials = Material.objects.all().order_by('name')
    return render(request, 'quotes/material_list.html', {'materials': materials})


@login_required
def material_create(request):
    if request.method == 'POST':
        form = MaterialForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Material created successfully!')
            return redirect('material_list')
    else:
        form = MaterialForm()
    return render(request, 'quotes/material_form.html', {'form': form, 'action': 'Create'})

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
            project = Project(
                user=request.user,
                title=request.POST['title'],
                description=request.POST.get('description', ''),
                location=request.POST['location'],  # Add location
                status='pending',  # Set initial status
                project_type=request.POST['project_type'],
                area_size=request.POST['area_size'],
                project_element=request.POST['project_element']
            )
            project.save()
            messages.success(request, 'Project created successfully!')
            return redirect('project_list')
        except Exception as e:
            messages.error(request, f'Error creating project: {str(e)}')

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
        location = request.POST.get('location')  # Add this line
        project_type = request.POST.get('project_type')
        area_size = request.POST.get('area_size')
        project_element = request.POST.get('project_elements')

        # Update project
        project.title = title
        project.description = description
        project.location = location  # Add this line
        project.project_type = project_type
        project.area_size = area_size
        project.project_element = project_element
        project.save()

        messages.success(request, 'Project updated successfully!')
        return redirect('project_list')

    return render(request, 'quotes/project_edit.html', {'project': project})

@user_passes_test(lambda u: u.is_staff)
def material_edit(request, material_id):
    material = get_object_or_404(Material, id=material_id)
    if request.method == 'POST':
        form = MaterialForm(request.POST, instance=material)
        if form.is_valid():
            form.save()
            messages.success(request, 'Material updated successfully!')
            return redirect('material_list')
    else:
        form = MaterialForm(instance=material)
    return render(request, 'quotes/material_form.html', {'form': form, 'action': 'Edit'})

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
    pending_count = Project.objects.filter(status='pending').count()
    approved_count = Project.objects.filter(status='approved').count()
    declined_count = Project.objects.filter(status='declined').count()
    completed_count = Project.objects.filter(status='completed').count()

    context = {
        'pending_count': pending_count,
        'approved_count': approved_count,
        'declined_count': declined_count,
        'completed_count': completed_count,
    }
    return render(request, 'quotes/admin_dashboard.html', context)

@staff_member_required
def admin_pending_projects(request):
    projects = Project.objects.filter(status='pending').order_by('-created_at')
    context = {
        'projects': projects,
        'page_title': 'Pending Projects',
    }
    return render(request, 'quotes/admin_dashboard.html', context)

@staff_member_required
def admin_approved_projects(request):
    projects = Project.objects.filter(status='approved').order_by('-created_at')
    context = {
        'projects': projects,
        'page_title': 'Approved Projects',
    }
    return render(request, 'quotes/admin_dashboard.html', context)

@staff_member_required
def admin_declined_projects(request):
    projects = Project.objects.filter(status='declined').order_by('-created_at')
    context = {
        'projects': projects,
        'page_title': 'Declined Projects',
    }
    return render(request, 'quotes/admin_dashboard.html', context)

@staff_member_required
def admin_completed_projects(request):
    projects = Project.objects.filter(status='completed').order_by('-created_at')
    context = {
        'projects': projects,
        'page_title': 'Completed Projects',
    }
    return render(request, 'quotes/admin_dashboard.html', context)

@staff_member_required
def admin_user_management(request):
    users = User.objects.all().order_by('-date_joined')
    context = {
        'users': users,
        'page_title': 'User Management',
    }
    return render(request, 'quotes/admin_user_management.html', context)

@staff_member_required
def update_project_status(request, project_id):
    if request.method == 'POST':
        project = get_object_or_404(Project, id=project_id)
        new_status = request.POST.get('status')
        if new_status in dict(Project.STATUS_CHOICES):
            project.status = new_status
            project.save()
            messages.success(request, f'Project status updated to {project.get_status_display()}')
        else:
            messages.error(request, 'Invalid status')
    return redirect(request.META.get('HTTP_REFERER', 'admin_dashboard'))

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


@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    # Get all project elements and their materials
    project_elements = ProjectElement.objects.filter(project=project).prefetch_related('materials')

    elements_data = []
    total_project_cost = 0

    for element in project_elements:
        materials_data = []
        element_total = 0

        for material in element.materials.all():
            # Calculate material costs
            material_base_cost = material.quantity * material.unit_price
            markup_amount = material_base_cost * (material.markup_percentage / 100)
            total_with_markup = material_base_cost + markup_amount

            materials_data.append({
                'name': material.name,
                'quantity': material.quantity,
                'unit': material.unit,
                'unit_price': material.unit_price,
                'base_cost': material_base_cost,
                'markup_percentage': material.markup_percentage,
                'total_with_markup': total_with_markup
            })
            element_total += total_with_markup

        elements_data.append({
            'element_name': element.element_name,
            'materials': materials_data,
            'element_total': element_total
        })
        total_project_cost += element_total

    context = {
        'project': project,
        'elements_data': elements_data,
        'total_project_cost': total_project_cost
    }

    return render(request, 'quotes/project_detail.html', context)


@login_required
def manage_element_materials(request, element_id):
    project_element = get_object_or_404(ProjectElement, id=element_id)

    if request.method == 'POST':
        form = ElementMaterialForm(request.POST)
        if form.is_valid():
            element_material = form.save(commit=False)
            element_material.project_element = project_element
            element_material.save()
            messages.success(request, 'Material added successfully!')
            return redirect('project_detail', project_id=project_element.project.id)
    else:
        form = ElementMaterialForm()

    context = {
        'form': form,
        'project_element': project_element,
        'existing_materials': ElementMaterial.objects.filter(project_element=project_element)
    }
    return render(request, 'quotes/manage_element_materials.html', context)


def delete_element_material(request, element_material_id):
    element_material = get_object_or_404(ElementMaterial, id=element_material_id)
    project_id = element_material.project_element.project.id

    if request.method == 'POST':
        element_material.delete()
        messages.success(request, 'Material removed successfully!')

    return redirect('project_detail', project_id=project_id)

@staff_member_required
def admin_project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    ProjectElementFormSet = formset_factory(ProjectElementForm, extra=1)
    MaterialFormSet = formset_factory(MaterialForm, extra=1)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        element_formset = ProjectElementFormSet(request.POST, prefix='elements')
        material_formset = MaterialFormSet(request.POST, prefix='materials')

        if form.is_valid() and element_formset.is_valid() and material_formset.is_valid():
            project = form.save()

            # Save project elements
            ProjectElement.objects.filter(project=project).delete()
            for element_form in element_formset:
                if element_form.cleaned_data:
                    element = element_form.save(commit=False)
                    element.project = project
                    element.save()

            # Save materials
            project.materials.clear()
            for material_form in material_formset:
                if material_form.cleaned_data:
                    material = material_form.save(commit=False)
                    material.save()
                    project.materials.add(material)

            if request.is_ajax():
                return JsonResponse({'status': 'success'})
            return redirect('admin_project_list')
        else:
            if request.is_ajax():
                errors = {}
                if form.errors:
                    errors.update(form.errors)
                if element_formset.errors:
                    errors['elements'] = element_formset.errors
                if material_formset.errors:
                    errors['materials'] = material_formset.errors
                return JsonResponse({'status': 'error', 'errors': errors})

    else:
        form = ProjectForm(instance=project)
        element_formset = ProjectElementFormSet(prefix='elements', initial=[
            {'element_name': element.element_name, 'quantity': element.quantity}
            for element in project.projectelement_set.all()
        ])
        material_formset = MaterialFormSet(prefix='materials', initial=[
            {'name': material.name, 'quantity': material.quantity, 'unit_price': material.unit_price, 'markup_percentage': material.markup_percentage}
            for material in project.materials.all()
        ])

    context = {
        'project': project,
        'form': form,
        'element_formset': element_formset,
        'material_formset': material_formset,
    }
    return render(request, 'quotes/admin_project_detail.html', context)


@staff_member_required
def update_global_markup(request, project_id):
    if request.method == 'POST':
        project = get_object_or_404(Project, id=project_id)
        global_markup = request.POST.get('global_markup')
        try:
            global_markup = float(global_markup)
            for material in project.materials.all():
                material.markup_percentage = global_markup
                material.save()
            return JsonResponse({'status': 'success'})
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Invalid markup value'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def update_project_ajax(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    form = ProjectForm(request.POST, instance=project)
    ProjectElementFormSet = formset_factory(ProjectElementForm, extra=0)
    MaterialFormSet = formset_factory(MaterialForm, extra=0)
    element_formset = ProjectElementFormSet(request.POST, prefix='elements')
    material_formset = MaterialFormSet(request.POST, prefix='materials')

    if form.is_valid() and element_formset.is_valid() and material_formset.is_valid():
        project = form.save()

        # Save project elements
        ProjectElement.objects.filter(project=project).delete()
        for element_form in element_formset:
            if element_form.cleaned_data:
                element = element_form.save(commit=False)
                element.project = project
                element.save()

        # Save materials
        project.materials.clear()
        for material_form in material_formset:
            if material_form.cleaned_data:
                material = material_form.save(commit=False)
                material.save()
                project.materials.add(material)

        return JsonResponse({'status': 'success'})
    else:
        errors = {}
        if form.errors:
            errors.update(form.errors)
        if element_formset.errors:
            errors['elements'] = element_formset.errors
        if material_formset.errors:
            errors['materials'] = material_formset.errors
        return JsonResponse({'status': 'error', 'errors': errors})

