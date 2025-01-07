# Generated by Django 5.0.10 on 2024-12-17 00:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publisher', '0053_alter_geoserverpool_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='geoserverpublishchannel',
            name='create_cached_layer',
            field=models.BooleanField(blank=True, default=True),
        ),
        migrations.AddField(
            model_name='geoserverpublishchannel',
            name='expire_client_cache_after_n_seconds',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='geoserverpublishchannel',
            name='expire_server_cache_after_n_seconds',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]