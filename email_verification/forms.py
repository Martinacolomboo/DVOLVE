from django import forms

class RequestCodeForm(forms.Form):
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={
        'placeholder': 'tu@correo.com', 'class': 'input'
    }))

class VerifyCodeForm(forms.Form):
    code = forms.CharField(
        label='Código',
        min_length=6,
        max_length=6,
        error_messages={
            'required': 'Este campo es obligatorio.',
            'min_length': 'El código debe tener exactamente 6 dígitos.',
            'max_length': 'El código debe tener exactamente 6 dígitos.',
        },
        widget=forms.TextInput(attrs={
            'placeholder': '000000',
            'inputmode': 'numeric',
            # clase específica (evita colisiones con .input)
            'class': 'ev-code',
            # IMPORTANTE: NO incluir 'minlength' en attrs para evitar mensajes HTML5 del navegador
            # 'minlength': '6',  <-- NO lo pongas aquí
            'autocomplete': 'one-time-code',
        })
    )

class EmailRequestForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'ev-input',
            'placeholder': 'tu@correo.com',
            'required': True,
            'autofocus': True,
        })
    )