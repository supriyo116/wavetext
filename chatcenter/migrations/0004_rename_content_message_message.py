# Generated by Django 5.0.7 on 2024-09-16 18:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chatcenter', '0003_remove_message_group_alter_message_receiver_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='content',
            new_name='message',
        ),
    ]
