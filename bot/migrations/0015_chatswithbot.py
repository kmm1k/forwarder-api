# Generated by Django 4.2.4 on 2023-09-11 16:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0014_alter_tagforwarding_allowed_users'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatsWithBot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('chat_id', models.CharField(max_length=1000)),
                ('name', models.CharField(max_length=1000)),
            ],
            options={
                'ordering': ['created'],
            },
        ),
    ]
