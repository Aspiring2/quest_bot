# Generated by Django 4.2.4 on 2024-12-14 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0003_userprogress_remove_poem_task_remove_puzzle_task_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='location',
            options={'ordering': ['order']},
        ),
        migrations.AlterModelOptions(
            name='task',
            options={'ordering': ['order']},
        ),
        migrations.AddField(
            model_name='location',
            name='order',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='task',
            name='order',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
