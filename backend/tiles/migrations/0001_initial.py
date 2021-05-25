# Generated by Django 3.0.5 on 2020-05-25 16:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cubes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('description', models.TextField(null=True)),
                ('link', models.TextField(max_length=255)),
                ('sequence', models.IntegerField()),
                ('photo_url', models.TextField(max_length=255)),
                ('cube', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cubes.Cube')),
            ],
            options={
                'db_table': 'tile',
            },
        ),
        migrations.CreateModel(
            name='TileComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('parent_id', models.IntegerField(default=0, null=True)),
                ('comment', models.TextField(null=True)),
                ('tile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tiles.Tile')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tile_comment', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TileFavorites',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tiles.Tile')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tile_like', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TileCommentFavorite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tiles.TileComment')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HashTags',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('tag', models.CharField(max_length=255)),
                ('tile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tiles.Tile')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]