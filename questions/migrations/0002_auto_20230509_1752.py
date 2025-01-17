# Generated by Django 3.2.9 on 2023-05-09 14:52

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0004_alter_user_language_code"),
        ("questions", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="question",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now,
                verbose_name="Создан",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="question",
            name="msg_id",
            field=models.BigAutoField(
                primary_key=True, serialize=False, verbose_name="Номер сообщения"
            ),
        ),
        migrations.AlterField(
            model_name="question",
            name="text",
            field=models.TextField(verbose_name="Вопрос"),
        ),
        migrations.AlterField(
            model_name="question",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.DO_NOTHING,
                to="users.user",
                verbose_name="Отправитель",
            ),
        ),
    ]
