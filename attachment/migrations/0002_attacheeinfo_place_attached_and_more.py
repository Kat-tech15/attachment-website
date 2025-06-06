# Generated by Django 5.1.3 on 2025-05-16 18:57

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attachment', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='attacheeinfo',
            name='place_attached',
            field=models.CharField(default=django.utils.timezone.now, max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='attacheefirminfo',
            name='slots',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='attacheeinfo',
            name='phone_number',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='tenantsinfo',
            name='phone_number',
            field=models.IntegerField(),
        ),
    ]
