# Generated by Django 3.0.5 on 2020-07-29 04:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tiles', '0005_auto_20200729_1125'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tilecomment',
            name='updated_at',
            field=models.DateTimeField(null=True),
        ),
    ]