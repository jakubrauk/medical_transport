# Generated by Django 4.2.6 on 2023-11-15 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base_app', '0002_paramedic_dispositor'),
    ]

    operations = [
        migrations.AddField(
            model_name='paramedic',
            name='last_lat_lng_update',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
