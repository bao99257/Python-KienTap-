# Generated by Django 4.2.23 on 2025-07-06 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0010_merge_20250706_2212"),
    ]

    operations = [
        migrations.AlterField(
            model_name="refundrequest",
            name="is_approved",
            field=models.BooleanField(default=None, null=True),
        ),
    ]
