# Generated by Django 5.1.4 on 2024-12-28 06:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mambaling', '0010_remove_clearancerequest_notification_sent_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='clearancerequest',
            name='notification_sent',
            field=models.BooleanField(default=False),
        ),
    ]
