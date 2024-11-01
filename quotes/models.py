from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
        ('completed', 'Completed'),
        ('pending', 'Pending Admin Review'),
        ('quoted', 'Quotation Provided'),
        ('approved', 'Approved by Admin'),
        ('declined', 'Declined by Admin'),
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
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    project_type = models.CharField(max_length=100, choices=PROJECT_TYPES)
    area_size = models.DecimalField(max_digits=10, decimal_places=2, help_text="Area size in square meters")
    project_element = models.CharField(max_length=100, choices=PROJECT_ELEMENTS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    materials = models.ManyToManyField('Material', through='ProjectMaterial')
    admin_approved = models.BooleanField(default=False)
    customer_approved = models.BooleanField(default=False)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    admin_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"

class Material(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=0)
    markup_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    unit = models.CharField(max_length=20, default='')

    def __str__(self):
        return self.name

class ProjectElement(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    element_name = models.CharField(max_length=100)
    materials = models.ManyToManyField(Material, through='ElementMaterial')

    def __str__(self):
        return f'{self.element_name} for {self.project.title}'

    def get_total_cost(self):
        total = 0
        for element_material in self.elementmaterial_set.all():
            total += element_material.get_total_with_markup()
        return total

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

class Pricing(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)

    def __str__(self):
        return f'Pricing for {self.project.title}'

class Quotation(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Quotation for {self.project.title}'

class ProjectMaterial(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    markup_percentage = models.DecimalField(max_digits=5, decimal_places=2)