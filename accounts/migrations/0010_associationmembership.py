# Generated by Django 3.1.4 on 2020-12-14 10:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_auto_20201213_1408'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssociationMembership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('membership_time', models.DurationField(verbose_name='membership time ')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.member', verbose_name='member')),
            ],
        ),
    ]