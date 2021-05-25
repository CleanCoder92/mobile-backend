# Generated by Django 3.0.5 on 2020-07-29 03:32

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('cubes', '0004_cubecomment_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='cubecomment',
            name='updated_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='cubecomment',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]