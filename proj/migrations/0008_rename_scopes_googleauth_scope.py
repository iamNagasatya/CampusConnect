# Generated by Django 3.2.2 on 2024-03-11 12:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proj', '0007_googleauth'),
    ]

    operations = [
        migrations.RenameField(
            model_name='googleauth',
            old_name='scopes',
            new_name='scope',
        ),
    ]
