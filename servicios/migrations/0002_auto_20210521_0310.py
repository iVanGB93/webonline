# Generated by Django 3.0.5 on 2021-05-21 07:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servicios', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='estadoservicio',
            name='emby_sync',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='estadoservicio',
            name='ftp_sync',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='estadoservicio',
            name='int_sync',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='estadoservicio',
            name='jc_sync',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='oper',
            name='sync',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='recarga',
            name='sync',
            field=models.BooleanField(default=False),
        ),
    ]