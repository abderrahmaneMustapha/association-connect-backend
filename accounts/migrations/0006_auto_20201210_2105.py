# Generated by Django 3.1.4 on 2020-12-10 20:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_auto_20201208_2309'),
    ]

    operations = [
        migrations.AlterField(
            model_name='association',
            name='description',
            field=models.TextField(blank=True, max_length=1500, null=True, verbose_name='description of the association'),
        ),
    ]