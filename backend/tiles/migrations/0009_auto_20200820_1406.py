# Generated by Django 2.2.15 on 2020-08-20 06:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tiles', '0008_auto_20200820_1357'),
    ]

    operations = [
        migrations.AlterField(
            model_name='history',
            name='comment',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
