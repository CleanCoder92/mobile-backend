# Generated by Django 2.2.15 on 2020-08-20 05:57

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('tiles', '0007_auto_20200729_2047'),
    ]

    operations = [
        migrations.AlterField(
            model_name='history',
            name='comment',
            field=models.CharField(default=django.utils.timezone.now, max_length=255),
            preserve_default=False,
        ),
    ]
