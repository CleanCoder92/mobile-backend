# Generated by Django 3.0.5 on 2020-05-25 17:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tiles', '0002_auto_20200526_0100'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tilecomment',
            name='parent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='tiles.TileComment'),
        ),
    ]