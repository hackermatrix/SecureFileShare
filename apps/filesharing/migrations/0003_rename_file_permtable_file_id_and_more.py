# Generated by Django 4.2.5 on 2023-09-17 07:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('filesharing', '0002_permtable'),
    ]

    operations = [
        migrations.RenameField(
            model_name='permtable',
            old_name='File',
            new_name='File_id',
        ),
        migrations.RenameField(
            model_name='permtable',
            old_name='Requester',
            new_name='Requester_id',
        ),
    ]