# Generated by Django 3.2.2 on 2024-03-23 11:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('proj', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='gauth',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='who', to='proj.googleauth'),
        ),
    ]
