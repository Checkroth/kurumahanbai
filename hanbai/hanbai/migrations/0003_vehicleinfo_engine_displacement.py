# Generated by Django 3.1.5 on 2021-02-01 04:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hanbai', '0002_auto_20210130_0031'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicleinfo',
            name='engine_displacement',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='排気量cc'),
        ),
    ]
