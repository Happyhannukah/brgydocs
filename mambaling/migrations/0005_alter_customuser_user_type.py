# Generated by Django 5.0.6 on 2024-12-13 01:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mambaling', '0004_mambaling'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='user_type',
            field=models.CharField(choices=[('superuser', 'Superuser'), ('admin', 'Admin'), ('user', 'User')], default='user', help_text='Defines the role of the user in the system.', max_length=20),
        ),
    ]
