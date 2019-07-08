# -*- coding: utf-8 -*-
from common.mymako import render_mako_context, render_json

from home_application.unins.ESB import ESBComponentApi, ESBApi
import time
from django.db import transaction
from home_application import models
import json
import datetime
from common.log import logger


def job_exec(biz_name, handle_user, t_script_data, contents_name, biz_id, records, script_content=None, script_params=None,script_type=None,module_name=None):
    response = {
    }
    ip_list = []
    ip_clouds = records.split(',')
    for ip_cloud_string in ip_clouds:
        ip_cloud = ip_cloud_string.split('|')
        dict = {'ip': ip_cloud[0], 'bk_cloud_id': ip_cloud[1]}
        ip_list.append(dict)
    try:
        job_exec_result = ESBComponentApi().fast_execute_script(biz_id, script_content=script_content,
                                                                ip_list=ip_list,script_param=script_params,script_type=script_type)
        if job_exec_result['result']:
            job_instance_id = job_exec_result['data']['job_instance_id']
            job_instance_name = job_exec_result['data']['job_instance_name']
            response['result'] = True
            response['code'] = 0
            response['message'] = ''
            response['data'] = {}
            response['data']['job_instance_id'] = job_instance_id
            response['data']['job_instance_name'] = job_instance_name
            # biz_name_data = ESBComponentApi().the_biz_name(biz_id)
            # biz_name = biz_name_data['']
            job_data = models.T_RECORDS_TASK.objects.create(
                handle_user=handle_user,
                t_script_data=t_script_data,
                ips=records,
                script_name=contents_name,
                biz_name=biz_name,
                script_instance_id=job_exec_result['data']['job_instance_id'],
                status=1,
                module_name=module_name,
                begin_time=datetime.datetime.now(),
                script_parms=script_params
            )
            # bug 周期获取脚本结果每次等待1秒，获取30次
            while True:
                job_data_result = ESBComponentApi().get_job_instance_log(biz_id, job_instance_id)
                logger.info(job_data_result)
                if job_data_result['data'][0]['status'] == 3 or job_data_result['data'][0]['status'] == 4:
                    result = job_data_result['data'][0]['step_results'][0]['ip_logs']
                    for is_data in result:
                        ip = is_data['ip']
                        # if is_data['log_content'] != u'':
                        job_content_log = is_data['log_content']
                        models.T_PC_LOG.objects.create(
                            execution_instance=job_data,
                            execution_ip=ip,
                            execution_content=job_content_log,
                            begin_time=datetime.datetime.now(),
                            script_name=job_data.script_name
                        )
                    job_data.script_instance_id = job_instance_id
                    job_data.save()
                    break

        else:
            response['result'] = False
            response['code'] = 1
            response['message'] = job_exec_result['message']
            response['data'] = {}
    except Exception as e:
        response['result'] = False
        response['code'] = 1
        response['message'] = e
        response['data'] = {}
    return response


def time_script():
    script_job = models.T_RECORDS_TASK.objects.filter(status=0, is_delete=0)
    if script_job.count() != 0:
        for job_data in script_job:
            script_data = job_data.t_script_data
            ip_list = []
            ip_clouds = script_data.ip_list_all.split(',')
            for ip_cloud_string in ip_clouds:
                ip_cloud = ip_cloud_string.split('|')
                dict_data = {'ip': ip_cloud[0], 'bk_cloud_id': ip_cloud[1]}
                ip_list.append(dict_data)
            script_params = job_data.script_parms
            script_type = 1
            job_exec_result = ESBComponentApi().fast_execute_script(script_data.select_business, script_content=script_data.script_data,
                                                                    ip_list=ip_list, script_param=script_params,
                                                                    script_type=script_type)
            if job_exec_result['result']:
                biz_id = int(job_data.biz_name)
                job_instance_id = int(job_exec_result['data']['job_instance_id'])
                while True:
                    job_data_result = ESBComponentApi().get_job_instance_log(biz_id, job_instance_id)
                    logger.info(job_data_result)
                    if job_data_result['data'][0]['status'] == 3 or job_data_result['data'][0]['status'] == 4:
                        result = job_data_result['data'][0]['step_results'][0]['ip_logs']
                        for is_data in result:
                            ip = is_data['ip']
                            # if is_data['log_content'] != u'':
                            job_content_log = is_data['log_content']
                            models.T_PC_LOG.objects.create(
                                execution_instance=job_data,
                                execution_ip=ip,
                                execution_content=job_content_log,
                                begin_time=datetime.datetime.now(),
                                script_name=job_data.script_name
                            )
                        job_data.script_instance_id = job_instance_id
                        job_data.save()
                        break



