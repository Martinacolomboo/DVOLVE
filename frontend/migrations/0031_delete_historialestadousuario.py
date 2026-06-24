from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("frontend", "0030_questionario_fecha_vencimiento_plan"),
    ]

    operations = [
        migrations.DeleteModel(
            name="HistorialEstadoUsuario",
        ),
    ]
