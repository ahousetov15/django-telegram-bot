# Generated by Django 3.2.9 on 2023-05-21 21:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0006_auto_20230509_1851"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="first_name",
            field=models.CharField(
                blank=True, max_length=256, null=True, verbose_name="Имя"
            ),
        ),
    ]
