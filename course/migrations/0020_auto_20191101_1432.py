# Generated by Django 2.0 on 2019-11-01 06:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0019_auto_20191031_0745'),
    ]

    operations = [
        migrations.AddField(
            model_name='examples',
            name='example_tw',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='例句中文'),
        ),
        migrations.AlterField(
            model_name='examples',
            name='words',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.Words', verbose_name='單字名稱'),
        ),
    ]
