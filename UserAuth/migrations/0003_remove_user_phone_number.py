# Generated by Django 5.1 on 2024-10-07 06:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('UserAuth', '0002_alter_user_phone_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='phone_number',
        ),
    ]
