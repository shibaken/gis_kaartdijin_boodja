from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0055_add_timestamps_to_allowed_crs'),
    ]

    operations = [
        migrations.AlterField(
            model_name='catalogueentry',
            name='default_crs',
            field=models.ForeignKey(
                blank=True,
                help_text='Expected CRS for uploaded spatial files. If set, uploads with a different CRS will be declined, and GeoTIFFs whose CRS GeoServer cannot identify are published with this CRS.',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='catalogue_entries',
                to='catalogue.allowedcrs',
            ),
        ),
    ]
