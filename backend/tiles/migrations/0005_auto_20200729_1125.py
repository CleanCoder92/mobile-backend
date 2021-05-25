# Generated by Django 3.0.5 on 2020-07-29 03:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tiles', '0004_history'),
    ]

    operations = [
        migrations.AddField(
            model_name='tile',
            name='video_embed_code',
            field=models.TextField(max_length=255, null=True),
        ),
        migrations.AlterModelTable(
            name='hashtags',
            table='tile-hashtags',
        ),
    ]
