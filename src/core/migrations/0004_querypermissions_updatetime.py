# Generated by Django 2.0.1 on 2018-12-12 04:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_sqlorder_delete_yn'),
    ]

    operations = [
        migrations.AddField(
            model_name='querypermissions',
            name='updatetime',
            field=models.DateTimeField(auto_now=True, verbose_name='最后修改日期'),
        ),
    ]
