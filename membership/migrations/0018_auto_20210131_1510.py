# Generated by Django 3.1.4 on 2021-01-31 14:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('membership', '0017_auto_20210131_1146'),
    ]

    operations = [
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=125, verbose_name='choice text')),
                ('name', models.CharField(max_length=125, verbose_name='choice html name or value')),
            ],
        ),
        migrations.AddField(
            model_name='field',
            name='choices',
            field=models.ManyToManyField(to='membership.Choice'),
        ),
    ]
