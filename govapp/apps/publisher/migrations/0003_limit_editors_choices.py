# Generated by Django 3.2.17 on 2023-02-09 05:46

from django.conf import settings
from django.db import migrations, models
import govapp.apps.accounts.utils


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('publisher', '0002_add_publish_format'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publishentry',
            name='editors',
            field=models.ManyToManyField(blank=True, limit_choices_to=govapp.apps.accounts.utils.limit_to_administrators, to=settings.AUTH_USER_MODEL),  # type: ignore[arg-type]
        ),
    ]