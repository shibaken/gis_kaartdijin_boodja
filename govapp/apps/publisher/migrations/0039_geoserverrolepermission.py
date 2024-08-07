# Generated by Django 3.2.25 on 2024-05-21 06:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('publisher', '0038_auto_20240521_1226'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeoServerRolePermission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('read', models.BooleanField(default=False)),
                ('write', models.BooleanField(default=False)),
                ('admin', models.BooleanField(default=False)),
                ('active', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('geoserver_role', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='publisher.geoserverrole')),
                ('workspace', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='publisher.workspace')),
            ],
            options={
                'verbose_name': 'GeoServer RolePermission',
                'verbose_name_plural': 'GeoServer RolePermissions',
            },
        ),
    ]
