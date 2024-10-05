# store/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re
from django.core.validators import validate_email

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label='Keresztnév')
    last_name = forms.CharField(max_length=30, required=True, label='Vezetéknév')
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
   
    def clean_email(self):
        email = self.cleaned_data.get('email')
        validate_email(email)  # Beépített validátor használata
        return email


    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if len(password) < 8:
            raise ValidationError("A jelszónak legalább 8 karakter hosszúnak kell lennie.")
        if not re.search(r'\d', password):  # Ellenőrizzük, hogy tartalmaz-e számot
            raise ValidationError("A jelszónak tartalmaznia kell legalább egy számot.")
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

    

   
