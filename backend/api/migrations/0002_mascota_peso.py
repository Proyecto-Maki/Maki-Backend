# Generated by Django 5.1.4 on 2025-01-03 00:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mascota',
            name='peso',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=3),
            preserve_default=False,
        ),
    ]
