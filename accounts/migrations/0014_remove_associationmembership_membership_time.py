# Generated by Django 3.1.4 on 2020-12-30 13:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_association_slug'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='associationmembership',
            name='membership_time',
        ),
    ]