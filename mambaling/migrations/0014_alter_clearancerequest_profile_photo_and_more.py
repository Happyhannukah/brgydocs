# Generated by Django 5.1.4 on 2025-01-08 10:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mambaling', '0013_proofofresidency'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clearancerequest',
            name='profile_photo',
            field=models.ImageField(blank=True, null=True, upload_to='profile_photos/'),
        ),
        migrations.AlterField(
            model_name='clearancerequest',
            name='proof_of_residency',
            field=models.FileField(blank=True, null=True, upload_to='proof_of_residency/'),
        ),
        migrations.AlterField(
            model_name='clearancerequest',
            name='purpose',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='clearancerequest',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Declined', 'Declined')], default='Barangay Clearance', max_length=20),
        ),
    ]
