# Generated by Django 3.0.5 on 2024-02-12 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servicios', '0004_auto_20211013_1143'),
    ]

    operations = [
        migrations.AddField(
            model_name='recarga',
            name='creator',
            field=models.CharField(default='0n3', max_length=20),
        ),
    ]