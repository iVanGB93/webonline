# Generated by Django 3.0.5 on 2021-08-07 00:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sorteo', '0011_sorteo_sync'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sorteo',
            name='mes',
            field=models.CharField(default=8, max_length=10),
        ),
        migrations.AlterField(
            model_name='sorteodetalle',
            name='mes',
            field=models.CharField(default=8, max_length=10),
        ),
    ]