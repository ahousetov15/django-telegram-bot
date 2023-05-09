# Generated by Django 3.2.9 on 2023-05-09 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chats', '0002_alter_chats_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chats',
            name='chat_id',
            field=models.BigAutoField(primary_key=True, serialize=False, verbose_name='Номер чата'),
        ),
        migrations.AlterField(
            model_name='chats',
            name='chat_name',
            field=models.CharField(blank=True, max_length=1024, null=True, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='chats',
            name='is_support_chat',
            field=models.BooleanField(default=False, verbose_name='Чат поддержки'),
        ),
    ]
