# Generated by Django 2.2.15 on 2021-02-11 03:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cubes', '0008_auto_20200729_1234'),
    ]

    operations = [
        migrations.AddField(
            model_name='cube',
            name='is_published',
            field=models.BooleanField(default=False),
        ),
    ]
