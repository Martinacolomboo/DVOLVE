from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("frontend", "0031_delete_historialestadousuario"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="HistorialVencimientoPlan",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("fecha_anterior", models.DateField(blank=True, null=True)),
                ("fecha_nueva", models.DateField()),
                ("creado_en", models.DateTimeField(auto_now_add=True)),
                (
                    "questionario",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="historial_vencimientos",
                        to="frontend.questionario",
                    ),
                ),
                (
                    "realizado_por",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="extensiones_plan_realizadas",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-creado_en"],
            },
        ),
    ]
