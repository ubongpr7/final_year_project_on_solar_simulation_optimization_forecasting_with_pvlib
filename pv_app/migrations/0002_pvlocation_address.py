# Generated by Django 4.2.15 on 2024-08-25 10:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pv_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pvlocation',
            name='address',
            field=models.CharField(help_text='Enter address', max_length=120, null=True),
        ),
    ]
