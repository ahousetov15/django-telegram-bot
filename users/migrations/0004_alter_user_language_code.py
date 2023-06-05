# Generated by Django 3.2.9 on 2023-05-08 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0003_rm_unused_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="language_code",
            field=models.CharField(
                blank=True, help_text="Язык пользователя", max_length=8, null=True
            ),
        ),
    ]
