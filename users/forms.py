from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from users.models import CustomUser
from service.models import SupportDepartment, ServiceCategory

User = get_user_model()

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }


class CustomUserCreationForm(UserCreationForm):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('technician', 'Technician'),
        ('manager', 'Manager'),
    ]

    role = forms.ChoiceField(choices=ROLE_CHOICES, label="Role")

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone_number', 'department', 'staff_id', 'password1', 'password2', 'role']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class TechnicianCreationForm(UserCreationForm):
    departments = forms.ModelMultipleChoiceField(
        queryset=SupportDepartment.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Departments"
    )
    expertise = forms.ModelMultipleChoiceField(
        queryset=ServiceCategory.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Expertise"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'department', 'staff_id', 'password1', 'password2', 'departments', 'expertise']
