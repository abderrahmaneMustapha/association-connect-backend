# Generated by Django 3.1.4 on 2020-12-27 17:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('membership', '0006_auto_20201226_2152'),
    ]

    operations = [
        migrations.AlterField(
            model_name='form',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='associations/forms', verbose_name='form image'),
        ),
    ]
