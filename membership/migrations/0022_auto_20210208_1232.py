# Generated by Django 3.1.4 on 2021-02-08 11:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('membership', '0021_auto_20210208_1156'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fieldtype',
            name='html_name',
            field=models.SlugField(choices=[('short-text', 'text'), ('long-text', 'textarea'), ('number', 'number'), ('image', 'image'), ('file', 'file'), ('checkbox', 'checkbox'), ('radio', 'radio'), ('select', 'select')], max_length=225, null=True, verbose_name='html field name'),
        ),
        migrations.AlterField(
            model_name='fieldtype',
            name='name',
            field=models.CharField(choices=[('text', 'short-text'), ('textarea', 'long-text'), ('number', 'number'), ('image', 'image'), ('file', 'file'), ('checkbox', 'checkbox'), ('radio', 'radio'), ('select', 'select')], max_length=125, verbose_name='field name'),
        ),
    ]
