# -*- coding: utf-8 -*-

import base64
import sys
import datetime
import os

from common.mymako import render_mako_context, render_json
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage, InvalidPage
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import FileResponse

from home_application import models
from unins import ESB
from home_application.celery_tasks import async_run_script

reload(sys)
sys.setdefaultencoding('utf8')


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
                response['data']['list'] = ips
                response['data']['count'] = len(ips)
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


# 调用快速执行脚本
def run_inspect(request):
    '''
    执行脚本接口
    :param request:
    :return:
    '''

    # 创建一条记录
    # try:
        # 前端获取参数

    ips = request.GET.getlist('jiaoben_role')
    select_script = request.GET.get('select_script')
    select_business = request.GET.get('select_business')
    select_data = select_business.split(',')
    select_business = select_data[0]
    biz_name = select_data[1]
    ip_list_all = ','.join(ips)
    script_contents = models.T_C_SCRIPT.objects.get(id=select_script)
    script_data = base64.b64encode(script_contents.script_content.encode('utf-8'))
    contents_name = script_contents.name
    ip_list = ip_list_all
    module_name = script_contents.name
    script_type = 3
    handle_user = request.user.username
    t_script_data = models.T_SCRIPT_DATA.objects.create(
        ip_list_all=ip_list,
        contents_name=contents_name,
        select_business=select_business,
        script_type=script_type,
        module_name=module_name,
        script_data=script_data
    )
    async_run_script(handle_user, t_script_data, contents_name, select_business, ip_list, script_type=script_type, module_name=module_name, script_content=script_data)

    # except Exception, e:
    #     response = {
    #         'result': False,
    #         'code': 1,
    #         'message': u'执行脚本失败：%s' % e,
    #         'data': {},
    #     }
    return redirect(reverse(home))


# 新增模板
def add_module_html(request):
    result = job_data(request)
    all_pid = result.get('data')
    return render_mako_context(request, 'home_application/script_supervise.html', {'all_pid': all_pid})


# 新增模块的方法 django post带文件请求
@csrf_exempt
def add_module(request):
    if request.method == "POST":
        biz_id = int(request.POST.get('select_business2').split(',')[0])
        biz_name = request.POST.get('select_business2').split(',')[1]
        module_type = request.POST.get('module_type', '')
        module_name = request.POST.get('module_name', '')
        number = request.POST.get('number', '')

        # 存入文件
        obj = request.FILES.get('task_file', '')
        filename = 'home_application/upload/' + obj.name
        if os.path.exists(filename):
            os.remove(filename)
        fobj = open(filename, 'wb+')  # 打开上传文件
        for x in obj.chunks():
            fobj.write(x)  # request.FILES,文件专用
        fobj.close()

        module_data = models.TASK_MODULE.objects.create(
            biz_name=biz_name,
            biz_id=biz_id,
            module_name=module_name,
            module_type=module_type,
            hands_user=request.user.username,
            module_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            updata_hands_user=request.user.username,
            updata_module_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            is_delete=0
        )
        # wb = xlrd.open_workbook(filename=filename)
        # sheet1 = wb.sheet_by_index(0)
        # column_num = sheet1.nrows
        # for num in range(1, column_num):
        #     line_data = sheet1.row_values(num)
        #     models.T_SCRIPT_DATA.objects.create(
        #         task_module=module_data,
        #         operation_id=int(line_data[0]),
        #         operation=line_data[1],
        #         remarks=line_data[2],
        #         people_name=line_data[3],
        #         status=0
        #     )

        file_data = open(filename, 'rb')
        response = FileResponse(file_data)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="history_info.xls"'
    return redirect(reverse(home))
