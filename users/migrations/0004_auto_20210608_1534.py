# Generated by Django 3.0.5 on 2021-06-08 19:34

from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_profile_sync'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='imagen',
            field=models.ImageField(default='defaultUsuario.jpg', upload_to=users.models.upload_to, verbose_name='Image'),
        ),
    ]
