from django.contrib import admin
from .models import Pricing, Quotation, QuotationMaterial
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

class QuotationMaterialInline(admin.TabularInline):
    model = QuotationMaterial
    extra = 1


class QuotationMaterialInline(admin.TabularInline):
    model = QuotationMaterial
    extra = 1
    fields = ['material', 'quantity', 'unit_price', 'markup_percentage']

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        form = formset.form
        form.base_fields['material'].queryset = Material.objects.all()
        return formset


class QuotationAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'customer', 'total_amount', 'created_at']
    list_filter = ['project_type', 'created_at']
    search_fields = ['title', 'project__title', 'customer__username']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [QuotationMaterialInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('project', 'customer', 'title', 'location')
        }),
        ('Project Details', {
            'fields': ('description', 'project_type', 'area_size', 'project_element')
        }),
        ('Financial Details', {
            'fields': ('total_amount', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['project'].queryset = Project.objects.filter(status='pending')
        return form

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        quotation = form.instance
        total = sum(qm.get_total() for qm in quotation.quotationmaterial_set.all())
        quotation.total_amount = total
        quotation.save()