# Generated by Django 5.1.5 on 2025-01-21 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_problem_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='problem',
            name='language',
            field=models.CharField(max_length=200),
        ),
    ]
