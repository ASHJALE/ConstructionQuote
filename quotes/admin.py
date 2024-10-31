from django.contrib import admin
from .models import Project, ProjectElement, Material, Pricing, Quotation

admin.site.register(Project)
admin.site.register(ProjectElement)
admin.site.register(Material)
admin.site.register(Pricing)
admin.site.register(Quotation)