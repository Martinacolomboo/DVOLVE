from django import forms

class RequestCodeForm(forms.Form):
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={
        'placeholder': 'tu@correo.com', 'class': 'input'
    }))

class VerifyCodeForm(forms.Form):
    code = forms.CharField(label='Código', min_length=6, max_length=6,
                           widget=forms.TextInput(attrs={
                               'placeholder': '000000', 'inputmode': 'numeric', 'class': 'input'
                           }))
