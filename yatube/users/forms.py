from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model


User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = {
            'first_name', 
            'last_name', 
            'username', 
            'email'}

        widgets = {
        'username':forms.TextInput(attrs={'class':'form-control'}),
        'first_name':forms.TextInput(attrs={'class':'form-control', 'required':'required'}),
        'last_name':forms.TextInput(attrs={'class':'form-control', 'required':'required'}),
        'email':forms.EmailInput(attrs={'class':'form-control', 'required':'required'}),
        'password1':forms.PasswordInput(attrs={'class':'form-control'}),
        'password2':forms.PasswordInput(attrs={'class':'form-control'}),
    }
