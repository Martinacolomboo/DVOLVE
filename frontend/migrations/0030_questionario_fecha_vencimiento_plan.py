from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("frontend", "0029_historialestadousuario"),
    ]

    operations = [
        migrations.AddField(
            model_name="questionario",
            name="fecha_vencimiento_plan",
            field=models.DateField(blank=True, null=True),
        ),
    ]
