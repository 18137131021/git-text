# -*- coding: utf-8 -*-
from django.db import models


# 任务模板表
class TASK_MODULE(models.Model):
    module_name = models.CharField(verbose_name=u"模板名称", max_length=100)
    biz_name = models.CharField(verbose_name=u"业务名称", max_length=100)
    biz_id = models.CharField(verbose_name=u"业务id", max_length=100)
    module_type = models.CharField(verbose_name=u"模板类型", max_length=100)
    hands_user = models.CharField(verbose_name=u"创建者", max_length=100)
    module_time = models.CharField(verbose_name=u"创建时间", max_length=100)
    updata_hands_user = models.CharField(verbose_name=u"更新者", max_length=100)
    updata_module_time = models.CharField(verbose_name=u"更新时间", max_length=100)

    is_delete = models.IntegerField(verbose_name=u"是否删除", default=0)

    class Meta:
        verbose_name = u"任务模板"
        db_table = 'task_module'
