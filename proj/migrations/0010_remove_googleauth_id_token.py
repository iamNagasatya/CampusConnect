# Generated by Django 3.2.2 on 2024-03-12 05:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proj', '0009_alter_googleauth_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='googleauth',
            name='id_token',
        ),
    ]