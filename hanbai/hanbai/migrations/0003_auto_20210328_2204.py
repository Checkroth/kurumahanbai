# Generated by Django 3.1.5 on 2021-03-28 13:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hanbai', '0002_auto_20210211_1451'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_details',
            field=models.OneToOneField(default=1, help_text='お支払い明細', on_delete=django.db.models.deletion.PROTECT, to='hanbai.paymentdetails'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='extrafield',
            name='value_type',
            field=models.IntegerField(choices=[(1, 'String'), (2, 'Integer')], default=1),
        ),
        migrations.AlterField(
            model_name='itemization',
            name='special_discount',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='特別値引き (2)'),
        ),
        migrations.AlterField(
            model_name='itemization',
            name='vehicle_price',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='車輌本体価格 (1)'),
        ),
    ]
