# Generated by Django 4.2.15 on 2024-08-26 04:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pv_app', '0004_alter_pvlocation_options_pvsystem_pdc0_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='pvsystem',
            name='gamma_pdc',
            field=models.DecimalField(decimal_places=4, default=0.004, help_text='Temperature coefficient of power (gamma_pdc).', max_digits=5),
        ),
    ]
