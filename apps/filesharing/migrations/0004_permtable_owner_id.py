# Generated by Django 4.2.5 on 2023-09-17 12:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('filesharing', '0003_rename_file_permtable_file_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='permtable',
            name='Owner_id',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='owned_files', to=settings.AUTH_USER_MODEL),
        ),
    ]