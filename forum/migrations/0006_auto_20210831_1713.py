# Generated by Django 3.0.5 on 2021-08-31 21:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0005_auto_20210609_1853'),
    ]

    operations = [
        migrations.RenameField(
            model_name='publicacion',
            old_name='online',
            new_name='sync',
        ),
    ]
