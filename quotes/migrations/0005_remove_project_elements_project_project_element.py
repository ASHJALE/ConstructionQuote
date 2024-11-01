# Generated by Django 5.1.2 on 2024-11-01 08:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quotes', '0004_project_area_size_project_elements'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='elements',
        ),
        migrations.AddField(
            model_name='project',
            name='project_element',
            field=models.CharField(choices=[('walls', 'Walls'), ('roof', 'Roof'), ('flooring', 'Flooring'), ('second_floor', 'Second Floor'), ('swimming_pool', 'Swimming Pool'), ('electrical', 'Electrical'), ('windows_and_doors', 'Windows and Doors'), ('gardening', 'Gardening')], default=0, max_length=20),
            preserve_default=False,
        ),
    ]