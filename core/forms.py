from django import forms
from django.contrib.auth.models import User, Group
from .models import FarmerProfile,SupplierProfile, Product

ROLE_CHOICES = (
    ('Farmer', 'Farmer'),
    ('Supplier', 'Supplier'),
    ('Field Officer', 'Field Officer'),
)

class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password', 'required': True})
    )
    role = forms.ChoiceField(
        choices=ROLE_CHOICES, 
        widget=forms.Select(attrs={'class': 'form-control', 'required': True})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username', 'required': True}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email', 'required': True}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            group = Group.objects.get(name=self.cleaned_data['role'])
            user.groups.add(group)
        return user
    


class FarmerProfileForm(forms.ModelForm):
    class Meta:
        model = FarmerProfile
        fields = ['photo','full_name', 'phone', 'location', 'farm_size']
        

class SupplierProfileForm(forms.ModelForm):
    class Meta:
        model = SupplierProfile
        fields = ['photo','company_name', 'phone', 'location']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'stock',]
