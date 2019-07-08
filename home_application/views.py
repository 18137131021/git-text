# -*- coding: utf-8 -*-

from common.mymako import render_mako_context, render_json
from home_application import models
from unins import ESB
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage, InvalidPage


def dev_guide(request):
    """
    开发指引
    """
    return render_mako_context(request, '/home_application/dev_guide.html')


def contactus(request):
    """
    联系我们
    """
    return render_mako_context(request, '/home_application/contact.html')


# 进入首页
def home(request):
    """
    首页
    """
    all_script_task = models.TASK_MODULE.objects.filter(is_delete=0)
    #
    result = job_data(request)
    all_pid = result.get('data')
    # ip_data = ESB.ESBApi(request).search_host(biz_id=3)
    # ips = list()
    # for biz_info in ip_data['data']['info']:
    #     innip = biz_info['host']['bk_host_innerip']
    #     ips.append(innip)
    #
    # print ips
    paginator = Paginator(all_script_task, 2)  # Show 25 contacts per page

    page = request.GET.get('page')
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        contacts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        contacts = paginator.page(paginator.num_pages)
    return render_mako_context(request,
                               'home_application/search_tasks.html',
                               {'all_pid': all_pid,
                                'contacts': contacts})


# 获取业务
def job_data(request):
    """
    获取当前用户下的业务
    :param request:
    :return:
    """

    response = {}

    try:
        result = ESB.ESBApi(request).search_business()
        if result['result']:
            response['result'] = True
            response['code'] = 0
            response['message'] = 'success'
            response['data'] = {}
            if len(result['data']['info']) > 0:
                for item in result['data']['info']:
                    dic = {}
                    dic[item['bk_biz_id']] = item['bk_biz_name']
                    response['data'].update(dic)
            else:
                response['result'] = True
                response['code'] = 0
                response['message'] = u'该用户下无业务'
                response['data'] = {}
        else:
            response = result

    except Exception, e:
        response['result'] = False
        response['code'] = 1
        response['message'] = u'获取业务列表失败：%s' % e
        response['data'] = {}

    return response


# 查询集群
def search_colony(request):

    biz_id = int(request.GET.get('biz_id'))
    response = {}

    try:
        result = ESB.ESBApi(request).search_set(bk_biz_id=biz_id)
        if result['result']:
            response['result'] = True
            response['code'] = 0
            response['message'] = 'success'
            response['data'] = {}
            list = []
            if len(result['data']['info']) > 0:
                for item in result['data']['info']:
                    listDic = {}
                    listDic['set_id'] = item['bk_set_id']
                    listDic['set_name'] = item['bk_set_name']

                    list.append(listDic)

                response['data']['list'] = list
            else:
                response['result'] = True
                response['code'] = 0
                response['message'] = u'该用户下无业务'
                response['data'] = {}
        else:
            response = result

    except Exception, e:
        response['result'] = False
        response['code'] = 1
        response['message'] = u'获取业务列表失败：%s' % e
        response['data'] = {}

    return render_json(response)


# 根据条件查询主机
def search_pc(request):
    response = {
        'result': True,
        'message': 'success',
        'code': 0,
        'data': {}
    }
    biz_id = request.GET.get('biz_id')
    set_id = request.GET.get('set_id')
    biz_id = biz_id.split(',')[0]
    biz_id = int(biz_id)
    set_id = int(set_id)
    try:
        result = ESB.ESBApi(request).search_host(biz_id=biz_id, set_id=set_id)
        ips = list()
        if result['code'] == 0:
            if result['data']['count'] > 0:
                for biz_info in result['data']['info']:
                    listDic = dict()
                    listDic['hostname'] = biz_info['host']['bk_host_name']
                    listDic['ip'] = biz_info['host']['bk_host_innerip']
                    listDic['os_type'] = biz_info['host']['bk_os_type']
                    listDic['os_name'] = biz_info['host']['bk_os_name']
                    bk_cloud = biz_info['host']['bk_cloud_id']
                    listDic['area'] = bk_cloud[0]['bk_inst_name']
                    listDic['area_id'] = bk_cloud[0]['bk_inst_id']
                    ips.append(listDic)
            else:
                response = {
                    'result': True,
                    'message': u'该业务下无IP',
                    'code': 0,
                    'data': {}
                }
        else:
            response = result

    except Exception, e:
        response = {
            'result': False,
            'message': '%s' % e,
            'code': 1,
            'data': {}
        }

    return render_json(response)