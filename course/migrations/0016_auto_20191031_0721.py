# Generated by Django 2.0 on 2019-10-30 23:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0015_examples'),
    ]

    operations = [
        migrations.AlterField(
            model_name='examples',
            name='words',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.Words', verbose_name='單字名稱'),
        ),
    ]
