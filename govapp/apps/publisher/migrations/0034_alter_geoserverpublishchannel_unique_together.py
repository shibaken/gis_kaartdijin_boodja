# Generated by Django 3.2.25 on 2024-05-02 02:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('publisher', '0033_merge_20240502_1027'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='geoserverpublishchannel',
            unique_together=set(),
        ),
    ]
