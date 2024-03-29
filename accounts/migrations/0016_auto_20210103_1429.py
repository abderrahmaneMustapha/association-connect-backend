# Generated by Django 3.1.4 on 2021-01-03 13:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0015_associationmembership_membership_time'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='association',
            options={'permissions': (('update_association_info', 'Update association Info'), ('view_association_dashboard', 'View association dashboard'), ('add_association_member', 'Add an new association member'), ('delete_association_member', 'Delete association member'), ('view_association_member', 'View association member'), ('add_group', 'Add new group'))},
        ),
        migrations.AlterModelOptions(
            name='associationgroup',
            options={'permissions': (('add_group_member', 'Add an new group member'), ('delete_group_member', 'Delete group member'), ('view_group_member_info', 'View group member info'), ('update_group_info', 'Update group Info'), ('view_group_dashboard', 'View group dashboard'), ('delete_group', 'Delete group'))},
        ),
    ]
