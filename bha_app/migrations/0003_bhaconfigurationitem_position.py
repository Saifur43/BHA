# Generated by Django 5.0.2 on 2025-01-12 03:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bha_app', '0002_bhaconfiguration_bha_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='bhaconfigurationitem',
            name='position',
            field=models.FloatField(default=0),
        ),
    ]
