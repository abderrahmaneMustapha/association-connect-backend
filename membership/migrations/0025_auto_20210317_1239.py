# Generated by Django 3.1.4 on 2021-03-17 11:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('membership', '0024_auto_20210208_1252'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='costs',
            unique_together={('form', 'title')},
        ),
    ]
