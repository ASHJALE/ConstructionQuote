from django.contrib import admin
from .models import Pricing, Quotation
from .models import Project, ProjectElement, Material, ElementMaterial
from django import forms

class ElementMaterialInline(admin.TabularInline):
    model = ElementMaterial
    extra = 1

class ElementMaterialForm(forms.ModelForm):
    class Meta:
        model = ElementMaterial
        fields = ['material', 'quantity', 'markup_percentage']
        widgets = {
            'material': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'markup_percentage': forms.NumberInput(attrs={'class': 'form-control'})
        }
class ProjectElementAdmin(admin.ModelAdmin):
    inlines = [ElementMaterialInline]
    list_display = ['element_name', 'project']

class MaterialAdmin(admin.ModelAdmin):
    list_display = ['name', 'unit_price', 'unit', 'markup_percentage']
    search_fields = ['name']
admin.site.register(Project)
admin.site.register(ProjectElement)
admin.site.register(Material)
admin.site.register(Pricing)
admin.site.register(Quotation)