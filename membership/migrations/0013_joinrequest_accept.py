# Generated by Django 3.1.4 on 2021-01-05 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('membership', '0012_auto_20210104_1356'),
    ]

    operations = [
        migrations.AddField(
            model_name='joinrequest',
            name='accept',
            field=models.BooleanField(default=False, verbose_name='accept this join request'),
        ),
    ]
