# Generated by Django 5.1.2 on 2024-11-01 17:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quotes', '0007_project_location_project_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='material',
            name='markup_percentage',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
        migrations.AddField(
            model_name='material',
            name='quantity',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='material',
            name='unit',
            field=models.CharField(default='', max_length=20),
        ),
    ]
