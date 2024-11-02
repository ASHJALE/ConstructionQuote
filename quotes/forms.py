from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Project, Material, Quotation, QuotationMaterial, ProjectElement

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your Gmail address'
        })
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username'
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if not email.endswith('@gmail.com'):
            raise forms.ValidationError("Please use a Gmail address.")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'location', 'project_type', 'area_size', 'status', 'project_element']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter project title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter project description'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter location'}),
            'project_type': forms.Select(attrs={'class': 'form-control'}),
            'area_size': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'project_element': forms.Select(attrs={'class': 'form-control'}),
        }

class ProjectElementForm(forms.ModelForm):
    class Meta:
        model = ProjectElement
        fields = ['element_name']
        widgets = {
            'element_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter element name'})
        }

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['name', 'description', 'unit_price', 'quantity', 'markup_percentage', 'unit']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter material name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter description'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'markup_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter unit (e.g., pcs, kg, m)'}),
        }

class QuotationForm(forms.ModelForm):
    quantities = forms.CharField(required=False, widget=forms.HiddenInput())
    unit_prices = forms.CharField(required=False, widget=forms.HiddenInput())
    markups = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Quotation
        fields = ('project', 'customer', 'title', 'location', 'description', 'project_type',
                 'area_size', 'project_element', 'materials', 'admin_notes', 'total_amount', 'status')
        widgets = {
            'customer': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True,
                'placeholder': 'Enter quotation title'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True,
                'placeholder': 'Enter location'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'required': True,
                'placeholder': 'Enter description'
            }),
            'project_type': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'area_size': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'required': True
            }),
            'project_element': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'materials': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'required': True
            }),
            'admin_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter admin notes'
            }),
            'total_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'readonly': True,
                'id': 'total_amount'
            }),
            'project': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            if user.is_staff:
                self.fields['project'].queryset = Project.objects.all()
            else:
                self.fields['project'].queryset = Project.objects.filter(user=user)
        else:
            self.fields['project'].queryset = Project.objects.none()

class QuotationMaterialForm(forms.ModelForm):
    class Meta:
        model = QuotationMaterial
        fields = ['material', 'quantity', 'unit_price', 'markup_percentage']
        widgets = {
            'material': forms.Select(attrs={'class': 'form-control material-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'markup_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['material'].queryset = Material.objects.all().order_by('name')