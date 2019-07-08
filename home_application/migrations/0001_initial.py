# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TASK_MODULE',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('module_name', models.CharField(max_length=100, verbose_name='\u6a21\u677f\u540d\u79f0')),
                ('biz_name', models.CharField(max_length=100, verbose_name='\u4e1a\u52a1\u540d\u79f0')),
                ('biz_id', models.CharField(max_length=100, verbose_name='\u4e1a\u52a1id')),
                ('module_type', models.CharField(max_length=100, verbose_name='\u6a21\u677f\u7c7b\u578b')),
                ('hands_user', models.CharField(max_length=100, verbose_name='\u521b\u5efa\u8005')),
                ('module_time', models.CharField(max_length=100, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('updata_hands_user', models.CharField(max_length=100, verbose_name='\u66f4\u65b0\u8005')),
                ('updata_module_time', models.CharField(max_length=100, verbose_name='\u66f4\u65b0\u65f6\u95f4')),
                ('is_delete', models.IntegerField(default=0, verbose_name='\u662f\u5426\u5220\u9664')),
            ],
            options={
                'db_table': 'task_module',
                'verbose_name': '\u4efb\u52a1\u6a21\u677f',
            },
        ),
    ]
