from django.db import models
from django.contrib.auth.models import User


class Project(models.Model):
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
        ('toilet_installation','Toilet Installation')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    project_type = models.CharField(max_length=100, choices=PROJECT_TYPES)
    area_size = models.DecimalField(max_digits=10, decimal_places=2, help_text="Area size in square meters")
    project_element = models.CharField(max_length=100, choices=PROJECT_ELEMENTS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class Pricing(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Example field
    description = models.TextField(blank=True)

    def __str__(self):
        return f'Pricing for {self.project.title}'

class ProjectElement(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    element_name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'Element: {self.element_name} for {self.project.title}'

class Quotation(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Quotation for {self.project.title}'

class Material(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name