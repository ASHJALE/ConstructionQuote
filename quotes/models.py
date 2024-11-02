from _pydecimal import Decimal
from django.db import models
from django.contrib.auth.models import User

class Material(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=0)
    markup_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    unit = models.CharField(max_length=20, default='')

    def __str__(self):
        return self.name

class Project(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('pending_review', 'Pending Admin Review'),
        ('quoted', 'Quotation Provided'),
        ('approved_admin', 'Approved by Admin'),
        ('approved_customer', 'Approved by Customer'),
        ('declined_admin', 'Declined by Admin'),
        ('declined_customer', 'Declined by Customer'),
        ('completed', 'Completed'),
        ('pending_admin_review', 'Pending Admin Review'),
    )

    PROJECT_TYPES = (
        ('framing', 'Framing'),
        ('window_and_door_installation', 'Window and Door Installation'),
        ('electrical', 'Electrical'),
        ('plumbing', 'Plumbing'),
    )

    PROJECT_ELEMENTS = (
        ('exterior_wall_framing', 'Exterior Wall Framing'),
        ('roof_framing', 'Roof Framing'),
        ('door_framing', 'Door Framing'),
        ('barn_door', 'Barn Door'),
        ('sliding_door', 'Sliding Door'),
        ('light_switches', 'Light Switches'),
        ('main_panel', 'Main Panel'),
        ('shower_fixture', 'Shower Fixture'),
        ('toilet_installation', 'Toilet Installation')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    project_type = models.CharField(max_length=100, choices=PROJECT_TYPES)
    area_size = models.DecimalField(max_digits=10, decimal_places=2, help_text="Area size in square meters")
    project_element = models.CharField(max_length=100, choices=PROJECT_ELEMENTS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    materials = models.ManyToManyField(Material, through='ProjectMaterial')
    admin_approved = models.BooleanField(default=False)
    customer_approved = models.BooleanField(default=False)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    admin_notes = models.TextField(blank=True)
    completion_date = models.DateTimeField(null=True, blank=True)
    completion_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"

    def calculate_total(self):
        total = Decimal('0')
        for project_material in self.projectmaterial_set.all():
            base_cost = project_material.quantity * project_material.unit_price
            markup_amount = base_cost * (project_material.markup_percentage / 100)
            total += base_cost + markup_amount
        self.total_cost = total
        return total

    def get_materials_data(self):
        materials_data = []
        for pm in self.projectmaterial_set.all():
            base_cost = pm.quantity * pm.unit_price
            markup_amount = base_cost * (pm.markup_percentage / 100)
            materials_data.append({
                'id': pm.material.id,
                'name': pm.material.name,
                'quantity': pm.quantity,
                'unit': pm.material.unit,
                'unit_price': pm.unit_price,
                'base_cost': base_cost,
                'markup_percentage': pm.markup_percentage,
                'total_with_markup': base_cost + markup_amount
            })
        return materials_data

class ProjectElement(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    element_name = models.CharField(max_length=100)
    materials = models.ManyToManyField(Material, through='ElementMaterial')

    def __str__(self):
        return f'{self.element_name} for {self.project.title}'

class ElementMaterial(models.Model):
    project_element = models.ForeignKey(ProjectElement, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    markup_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def get_total_cost(self):
        return self.quantity * self.material.unit_price

    def get_total_with_markup(self):
        total_cost = self.get_total_cost()
        markup_amount = total_cost * (self.markup_percentage / 100)
        return total_cost + markup_amount

    def __str__(self):
        return f'{self.material.name} for {self.project_element.element_name}'

class ProjectMaterial(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    markup_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Add this field

class Quotation(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    description = models.TextField()
    project_type = models.CharField(max_length=50, choices=Project.PROJECT_TYPES)
    area_size = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    project_element = models.CharField(max_length=50, choices=Project.PROJECT_ELEMENTS)
    materials = models.ManyToManyField(Material, through='QuotationMaterial')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    markup_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    materials_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    service_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    labor_costs = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    additional_markup = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('sent', 'Sent'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected')
        ],
        default='draft'
    )
    additional_markup_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['project'],
                name='unique_active_quotation_per_project'
            )
        ]
    def calculate_total(self):
        subtotal = self.materials_cost + self.service_fees + self.labor_costs
        markup_amount = subtotal * (self.additional_markup / 100)
        discount_amount = subtotal * (self.discount / 100)
        return subtotal + markup_amount - discount_amount

class QuotationMaterial(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    markup = models.DecimalField(max_digits=5, decimal_places=2)
    markup_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        unique_together = ['quotation', 'material']

    def get_total(self):
        return self.quantity * self.unit_price * (1 + self.markup/100)

    def total_price(self):
        base_price = self.quantity * self.unit_price
        markup = base_price * (self.markup_percentage / 100)
        return base_price + markup


class Pricing(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)

    def __str__(self):
        return f'Pricing for {self.project.title}'