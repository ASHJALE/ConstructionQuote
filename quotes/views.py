import json
from django.utils import timezone
from decimal import Decimal

from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail
from django.forms import formset_factory
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .admin import ElementMaterialForm
from .models import Project, Material, Pricing, ProjectElement, ElementMaterial, Quotation, ProjectMaterial

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Project, User
from .forms import (
    CustomUserCreationForm,
    ProjectForm,
    QuotationForm,
    QuotationMaterialForm,
    MaterialForm,
    ProjectElementForm
)
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

                # Check if user is superuser/staff and redirect accordingly
                if user.is_superuser or user.is_staff:
                    return redirect('admin_dashboard')
                else:
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
    project_materials = ProjectMaterial.objects.filter(project=project).select_related('material')

    if request.method == 'POST':
        try:
            # Get form data
            title = request.POST.get('title')
            description = request.POST.get('description')
            location = request.POST.get('location')
            project_type = request.POST.get('project_type')
            area_size = request.POST.get('area_size')
            project_element = request.POST.get('project_element')

            # Get materials data
            material_ids = request.POST.getlist('material_id[]')
            quantities = request.POST.getlist('quantity[]')
            unit_prices = request.POST.getlist('unit_price[]')
            markup_percentages = request.POST.getlist('markup_percentage[]')

            # Validate data lengths match
            if not (len(material_ids) == len(quantities) == len(unit_prices) == len(markup_percentages)):
                raise ValueError("Mismatched material data arrays")

            # Update project details
            project.title = title
            project.description = description
            project.location = location
            project.project_type = project_type
            project.area_size = Decimal(area_size)
            project.project_element = project_element

            # Calculate total project cost
            total_cost = Decimal('0.00')

            # Update project materials
            project.projectmaterial_set.all().delete()
            for i, material_id in enumerate(material_ids):
                if material_id:
                    try:
                        material = Material.objects.get(id=material_id)
                        quantity = Decimal(quantities[i])
                        unit_price = Decimal(unit_prices[i])
                        markup = Decimal(markup_percentages[i])

                        if quantity <= 0 or unit_price <= 0:
                            raise ValueError("Quantity and unit price must be positive")

                        # Calculate material total
                        material_cost = quantity * unit_price
                        markup_amount = material_cost * (markup / 100)
                        total_material_cost = material_cost + markup_amount

                        total_cost += total_material_cost

                        ProjectMaterial.objects.create(
                            project=project,
                            material=material,
                            quantity=quantity,
                            unit_price=unit_price,
                            markup_percentage=markup
                        )
                    except Material.DoesNotExist:
                        messages.error(request, f'Material with ID {material_id} not found')
                        continue

            # Update project total cost
            project.total_cost = total_cost
            project.save()

            messages.success(request, 'Project updated successfully!')
            return redirect('project_list')

        except Exception as e:
            messages.error(request, f'Error updating project: {str(e)}')
            print(f"Error in edit_project: {str(e)}")  # Debug print

    # Prepare context data
    materials_data = [{
        'id': pm.material.id,
        'name': pm.material.name,
        'quantity': pm.quantity,
        'unit': pm.material.unit,
        'unit_price': pm.unit_price,
        'base_cost': pm.quantity * pm.unit_price,
        'markup_percentage': pm.markup_percentage,
        'markup_amount': (pm.quantity * pm.unit_price) * (pm.markup_percentage / 100),
        'total_with_markup': (pm.quantity * pm.unit_price) * (1 + pm.markup_percentage / 100)
    } for pm in project_materials]

    total_project_cost = sum(m['total_with_markup'] for m in materials_data)

    context = {
        'project': project,
        'project_types': Project.PROJECT_TYPES,
        'project_elements': Project.PROJECT_ELEMENTS,
        'materials_data': materials_data,
        'available_materials': Material.objects.all(),
        'total_project_cost': total_project_cost,
    }
    return render(request, 'quotes/project_edit.html', context)

def calculate_material_totals(quantity, unit_price, markup_percentage):
    """Helper function to calculate material costs"""
    base_cost = Decimal(quantity) * Decimal(unit_price)
    markup_amount = base_cost * (Decimal(markup_percentage) / 100)
    total_with_markup = base_cost + markup_amount
    return {
        'base_cost': base_cost,
        'markup_amount': markup_amount,
        'total_with_markup': total_with_markup
    }

def get_material_details(request):
    material_id = request.GET.get('material_id')
    try:
        material = Material.objects.get(id=material_id)
        return JsonResponse({
            'status': 'success',
            'unit_price': float(material.unit_price),
            'unit': material.unit,
        })
    except Material.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Material not found'
        })
def request_quotation(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    materials = Material.objects.all()

    if request.method == 'POST':
        material_ids = request.POST.getlist('material[]')
        quantities = request.POST.getlist('quantity[]')
        units = request.POST.getlist('unit[]')
        prices = request.POST.getlist('price[]')
        notes = request.POST.get('notes')

        # Save the material requests
        for i in range(len(material_ids)):
            ProjectMaterial.objects.create(
                project=project,
                material_id=material_ids[i],
                quantity=quantities[i],
                unit=units[i],
                price_per_unit=prices[i]
            )

        project.status = 'pending'
        project.save()

        messages.success(request, 'Your quotation request has been submitted.')
        return redirect('project_list')

    context = {
        'project': project,
        'materials': materials,
    }
    return render(request, 'quotes/request_quotation.html', context)

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
    quotation_count = Quotation.objects.count()

    context = {
        'pending_count': pending_count,
        'approved_count': approved_count,
        'declined_count': declined_count,
        'completed_count': completed_count,
        'quotation_count': quotation_count,
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

@staff_member_required
def delete_user(request, user_id):
    user_to_delete = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        if user_to_delete.is_superuser:
            messages.error(request, "Cannot delete a superuser.")
        else:
            user_to_delete.delete()
            messages.success(request, f"User {user_to_delete.username} has been deleted.")
    return redirect('admin_user_management')


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

    # Create or update quotation
    quotation, created = Quotation.objects.get_or_create(
        project=project,
        customer=project.user,  # Add this line - use the project's user as the customer
        defaults={
            'total_amount': total_project_cost,
            'area_size': project.area_size
        }
    )
    if not created:
        quotation.total_amount = total_project_cost
        quotation.area_size = project.area_size
        quotation.save()

    context = {
        'project': project,
        'elements_data': elements_data,
        'total_project_cost': total_project_cost,
        'quotation': quotation
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
def admin_project_detail(request, pk):
    project = Project.objects.get(pk=pk)
    project_elements = project.elements.all()
    total_materials_cost = sum(material.get_total_cost for element in project_elements for material in element.materials.all())
    total_markup = sum(material.get_markup for element in project_elements for material in element.materials.all())
    total_project_cost = total_materials_cost + total_markup
    materials = project.materials.all()

    return render(request, 'quotes/admin_project_detail.html', {
        'project': project,
        'project_elements': project_elements,
        'total_materials_cost': total_materials_cost,
        'total_markup': total_markup,
        'total_project_cost': total_project_cost,
        'materials': materials,
    })

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


@staff_member_required
def admin_project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save()

            # Process elements and materials
            elements_data = json.loads(request.POST.get('elements_data', '[]'))
            ProjectElement.objects.filter(project=project).delete()
            for element_data in elements_data:
                element = ProjectElement.objects.create(
                    project=project,
                    element_name=element_data['name']
                )
                for material_data in element_data['materials']:
                    ElementMaterial.objects.create(
                        project_element=element,
                        material_id=material_data['id'],
                        quantity=material_data['quantity'],
                        markup_percentage=material_data['markup']
                    )

            messages.success(request, 'Project updated successfully.')
            return redirect('admin_project_list')
    else:
        form = ProjectForm(instance=project)

    context = {
        'form': form,
        'project': project,
        'elements': project.projectelement_set.prefetch_related('materials')
    }
    return render(request, 'quotes/admin_project_detail.html', context)

def customer_approve_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    if request.method == 'POST':
        project.customer_approved = True
        project.status = 'approved'
        project.save()
        messages.success(request, 'You have approved the project quotation.')
        return redirect('project_detail', project_id=project.id)
    return render(request, 'quotes/customer_approve_project.html', {'project': project})

def customer_decline_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    if request.method == 'POST':
        project.status = 'declined'
        project.save()
        messages.info(request, 'You have declined the project quotation.')
        return redirect('project_detail', project_id=project.id)
    return render(request, 'quotes/customer_decline_project.html', {'project': project})


def mark_project_completed(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if project.status != 'approved':
        messages.error(request, 'Only approved projects can be marked as completed.')
        return redirect('project_detail', project_id=project.id)

    if request.method == 'POST':
        completion_notes = request.POST.get('completion_notes', '')
        project.status = 'completed'
        project.completion_date = timezone.now()
        project.completion_notes = completion_notes
        project.save()

        # You might want to create a ProjectCompletion model to store more details
        # ProjectCompletion.objects.create(
        #     project=project,
        #     completed_by=request.user,
        #     completion_notes=completion_notes
        # )

        # Send notification to the customer
        send_project_completion_notification(project)

        messages.success(request, 'Project has been successfully marked as completed.')
        return redirect('project_detail', project_id=project.id)

    context = {
        'project': project,
        'checklist_items': [
            'All project elements have been completed according to specifications',
            'Quality checks have been performed and approved',
            'All materials and costs have been accounted for',
            'Customer has reviewed and accepted the completed work'
        ]
    }
    return render(request, 'quotes/mark_project_completed.html', context)

def send_project_completion_notification(project):
    subject = f'Project Completed: {project.title}'
    message = f"""
    Dear {project.user.username},

    We are pleased to inform you that your project has been successfully completed.

    Project Details:
    - Project ID: #{project.id}
    - Title: {project.title}
    - Type: {project.get_project_type_display()}
    - Location: {project.location}
    - Completion Date: {project.completion_date.strftime('%Y-%m-%d %H:%M')}

    Thank you for choosing our services. If you have any questions or need further assistance, please don't hesitate to contact us.

    Best regards,
    Your Project Team
    """
    from_email = 'delrosarioashleejale@gmail.com'  # Your Gmail address
    recipient_list = [project.user.email]  # Assuming the project has a user field with an email

    try:
        send_mail(
            subject,
            message,
            from_email,
            recipient_list,
            fail_silently=False,
        )
        print(f"Completion notification sent for project: {project.title}")
    except Exception as e:
        print(f"Failed to send completion notification for project: {project.title}. Error: {str(e)}")


def admin_create_quotation(request):
    pending_projects = Project.objects.filter(status='pending')

    if request.method == 'POST':
        project_id = request.POST.get('project')
        project = get_object_or_404(Project, id=project_id)

        total_amount = Decimal('0.00')
        admin_notes = request.POST.get('admin_notes', '')

        # Create the quotation
        quotation = Quotation.objects.create(
            project=project,
            total_amount=total_amount,
        )

        # Process each material
        for element in project.projectelement_set.all():
            for material in element.materials.all():
                quantity = Decimal(request.POST.get(f'quantity_{material.id}', 0))
                price = Decimal(request.POST.get(f'price_{material.id}', 0))
                markup = Decimal(request.POST.get(f'markup_{material.id}', 0))

                subtotal = quantity * price * (1 + markup / 100)
                total_amount += subtotal

                # Update or create ElementMaterial
                ElementMaterial.objects.update_or_create(
                    project_element=element,
                    material=material,
                    defaults={
                        'quantity': quantity,
                        'markup_percentage': markup
                    }
                )

        # Update the quotation with the final total amount
        quotation.total_amount = total_amount
        quotation.save()

        # Update project status and admin notes
        project.status = 'quoted'
        project.admin_notes = admin_notes
        project.save()

        messages.success(request, 'Quotation created successfully!')
        return redirect('admin_dashboard')

    context = {
        'pending_projects': pending_projects,
    }
    return render(request, 'quotes/admin_create_quotation.html', context)


@staff_member_required
def create_quotation(request):
    QuotationMaterialFormSet = formset_factory(QuotationMaterialForm, extra=1)

    if request.method == 'POST':
        form = QuotationForm(request.POST, user=request.user)  # Pass the user here
        material_formset = QuotationMaterialFormSet(request.POST)

        if form.is_valid() and material_formset.is_valid():
            quotation = form.save(commit=False)
            quotation.save()

            total_price = 0
            for material_form in material_formset:
                if material_form.cleaned_data:
                    material = material_form.save(commit=False)
                    material.quotation = quotation
                    material.save()
                    total_price += material.total_price

            quotation.total_price = total_price
            quotation.save()

            messages.success(request, 'Quotation created successfully!')
            return redirect('admin_dashboard')
    else:
        form = QuotationForm(user=request.user)  # Pass the user here too
        material_formset = QuotationMaterialFormSet()

    context = {
        'form': form,
        'material_formset': material_formset,
    }
    return render(request, 'quotes/admin_create_quotation.html',{'form': form})


def provide_quote(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        total_cost = request.POST.get('total_cost')
        admin_notes = request.POST.get('admin_notes')

        # Update the project with quote details
        project.total_cost = total_cost
        project.admin_notes = admin_notes
        project.status = 'quoted'  # Change status to quoted
        project.admin_approved = True
        project.save()

        messages.success(request, 'Quote has been provided successfully.')
        return redirect('admin_dashboard')

    context = {
        'project': project
    }
    return render(request, 'quotes/provide_quote.html', context)