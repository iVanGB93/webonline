# Generated by Django 3.0.5 on 2021-04-28 20:25

from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='imagen',
            field=models.ImageField(default='usuario/default.jpg', upload_to=users.models.upload_to, verbose_name='Image'),
        ),
    ]
