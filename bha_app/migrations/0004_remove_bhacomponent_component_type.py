# Generated by Django 5.0.2 on 2025-01-12 04:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bha_app', '0003_bhaconfigurationitem_position'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bhacomponent',
            name='component_type',
        ),
    ]
