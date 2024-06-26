# Generated by Django 3.2.25 on 2024-05-21 04:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publisher', '0036_alter_geoserverpublishchannel_publish_entry'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeoServerRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'GeoServer Role',
                'verbose_name_plural': 'GeoServer Roles',
            },
        ),
    ]
