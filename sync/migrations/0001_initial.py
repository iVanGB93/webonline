# Generated by Django 3.0.5 on 2021-07-23 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EstadoConexion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('servidor', models.CharField(max_length=25)),
                ('online', models.BooleanField(default=False)),
                ('ip_online', models.GenericIPAddressField(blank=True, null=True)),
                ('internet', models.BooleanField(default=False)),
                ('ip_internet', models.GenericIPAddressField(blank=True, null=True)),
                ('fecha_internet', models.DateTimeField(blank=True, null=True)),
                ('jc', models.BooleanField(default=False)),
                ('ip_jc', models.GenericIPAddressField(blank=True, null=True)),
                ('emby', models.BooleanField(default=False)),
                ('ip_emby', models.GenericIPAddressField(blank=True, null=True)),
                ('ftp', models.BooleanField(default=False)),
                ('ip_ftp', models.GenericIPAddressField(blank=True, null=True)),
                ('sync', models.BooleanField(default=False)),
            ],
        ),
    ]