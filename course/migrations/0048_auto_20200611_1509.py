# Generated by Django 3.0.6 on 2020-06-11 07:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0047_auto_20200611_1507'),
    ]

    operations = [
        migrations.AlterField(
            model_name='examples',
            name='words',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.Words', verbose_name='單字名稱'),
        ),
    ]
