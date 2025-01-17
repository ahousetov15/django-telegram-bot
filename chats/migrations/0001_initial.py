# Generated by Django 3.2.9 on 2023-05-08 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Chats",
            fields=[
                ("chat_id", models.BigAutoField(primary_key=True, serialize=False)),
                ("chat_name", models.CharField(blank=True, max_length=1024, null=True)),
                ("is_support_chat", models.BooleanField(default=False)),
            ],
        ),
    ]
