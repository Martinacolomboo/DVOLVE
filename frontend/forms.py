from django import forms
from django.contrib.auth.models import User

from .models import Questionario


class ClienteAdminForm(forms.ModelForm):
    first_name = forms.CharField(label="Nombre", max_length=150)
    last_name = forms.CharField(label="Apellido", max_length=150, required=False)
    email = forms.EmailField(label="Email de la clienta")
    fecha_vencimiento_plan = forms.DateField(
        label="Fecha de vencimiento del plan",
        required=True,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    class Meta:
        model = Questionario
        fields = [
            "fecha_vencimiento_plan",
            "health_conditions",
            "weight",
            "age",
            "height",
            "training_goal",
            "training_level",
            "training_place",
            "other_activity",
            "training_days",
            "sleep",
            "current_diet",
            "diet_restrictions",
            "diet_goal",
            "thyroid",
            "meals",
            "snacks",
            "meal_schedule",
            "hydration",
        ]
        labels = {
            "fecha_vencimiento_plan": "Fecha de vencimiento del plan",
            "health_conditions": "Lesiones o condiciones",
            "weight": "Peso (kg)",
            "age": "Edad",
            "height": "Altura (cm)",
            "training_goal": "Objetivo de entrenamiento",
            "training_level": "Nivel",
            "training_place": "Lugar de entrenamiento",
            "other_activity": "Actividad extra",
            "training_days": "Días de entrenamiento por semana",
            "sleep": "Sueño / descanso",
            "current_diet": "Alimentación actual",
            "diet_restrictions": "Restricciones alimentarias",
            "diet_goal": "Objetivo nutricional",
            "thyroid": "Tiroides",
            "meals": "Comidas por día",
            "snacks": "Colaciones / snacks",
            "meal_schedule": "Horarios de comida",
            "hydration": "Hidratación",
        }
        widgets = {
            "current_diet": forms.Textarea(attrs={"rows": 3}),
            "diet_goal": forms.TextInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

        for field_name in [
            "health_conditions",
            "training_goal",
            "training_level",
            "training_place",
            "other_activity",
            "sleep",
            "diet_restrictions",
            "thyroid",
            "snacks",
            "meal_schedule",
            "hydration",
        ]:
            self.fields[field_name].widget.attrs["class"] = "form-select"

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ya existe una usuaria con ese email.")
        return email


class AyudanteAdminForm(forms.Form):
    first_name = forms.CharField(label="Nombre", max_length=150)
    last_name = forms.CharField(label="Apellido", max_length=150, required=False)
    email = forms.EmailField(label="Email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ya existe una cuenta con ese email.")
        return email
