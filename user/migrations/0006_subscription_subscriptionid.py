# Generated by Django 4.2.9 on 2024-01-25 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_word_word_number_alter_word_word_limit'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='subscriptionid',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
