# Generated by Django 3.0.5 on 2024-02-12 19:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('control', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monthincome',
            name='gross_income',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='monthincome',
            name='income',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='monthincome',
            name='total_spent',
            field=models.IntegerField(default=0),
        ),
    ]
