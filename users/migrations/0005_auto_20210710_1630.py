# Generated by Django 3.0.5 on 2021-07-10 20:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20210608_1534'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificacion',
            name='sync',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='notificacion',
            name='tipo',
            field=models.CharField(choices=[('RECARGA', 'RGA'), ('PAGO', 'PAG'), ('ENVIO', 'ENV'), ('RECIBO', 'REC'), ('MENSAJE', 'MSJ'), ('REGISTRO', 'NEW')], max_length=10),
        ),
    ]