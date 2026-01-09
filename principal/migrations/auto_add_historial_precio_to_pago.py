from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('principal', '0008_planprecio_es_descuento'),
    ]

    operations = [
        migrations.AddField(
            model_name='pago',
            name='historial_precio',
            field=models.ForeignKey(
                to='principal.HistorialPrecioPlan',
                null=True,
                blank=True,
                on_delete=models.SET_NULL,
                help_text='Registro de precio vigente al momento del pago',
            ),
        ),
    ]
