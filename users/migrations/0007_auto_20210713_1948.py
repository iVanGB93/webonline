# Generated by Django 3.0.5 on 2021-07-13 23:48

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_notificacion_fecha'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notificacion',
            name='fecha',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 13, 23, 48, 30, 655584, tzinfo=utc)),
        ),
    ]
