# -*- coding: utf-8 -*-
"""
celery 任务示例

本地启动celery命令: python  manage.py  celery  worker  --settings=settings
周期性任务还需要启动celery调度命令：python  manage.py  celerybeat --settings=settings
"""
import datetime

from celery import task
from celery.schedules import crontab
from celery.task import periodic_task
from unins import job_exec
from common.log import logger


# 异步函数
@task
def async_run_script(handle_user, t_script_data, contents_name, biz_id, ip_list, script_type, module_name, script_content):
    '''
    异步执行脚本函数
    :param bk_biz_id:业务id
    :param ip_cloud_string: ip和云区域字符串（192.168.51.31|1,）
    :param script_content:  脚本内容数据是base64
    :param script_params:  脚本参数 数据是base64
    :return: 接口调用状态
    '''
    result = job_exec.job_exec(handle_user, t_script_data, contents_name, biz_id, ip_list, script_content=script_content, script_type=script_type, module_name=module_name)
    return result


@task()
def async_task(x, y):
    """
    定义一个 celery 异步任务
    """
    logger.error(u"celery 定时任务执行成功，执行结果：{:0>2}:{:0>2}".format(x, y))
    return x + y


def execute_task():
    """
    执行 celery 异步任务

    调用celery任务方法:
        task.delay(arg1, arg2, kwarg1='x', kwarg2='y')
        task.apply_async(args=[arg1, arg2], kwargs={'kwarg1': 'x', 'kwarg2': 'y'})
        delay(): 简便方法，类似调用普通函数
        apply_async(): 设置celery的额外执行选项时必须使用该方法，如定时（eta）等
                      详见 ：http://celery.readthedocs.org/en/latest/userguide/calling.html
    """
    now = datetime.datetime.now()
    logger.error(u"celery 定时任务启动，将在60s后执行，当前时间：{}".format(now))
    # 调用定时任务
    async_task.apply_async(args=[now.hour, now.minute], eta=now + datetime.timedelta(seconds=60))


@periodic_task(run_every=5)
def get_time():
    """
    celery 周期任务示例

    run_every=crontab(minute='*/5', hour='*', day_of_week="*")：每 5 分钟执行一次任务
    periodic_task：程序运行时自动触发周期任务
    """
    execute_task()
    now = datetime.datetime.now()
    # script_job = models.T_RECORDS_TASK.objects.all(is_delete=0)
    # if script_job.count() > 0:
    job_exec.time_script()
    logger.error(u"celery 周期任务调用成功，当前时间：{}".format(now))
