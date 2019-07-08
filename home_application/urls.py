# -*- coding: utf-8 -*-

from django.conf.urls import patterns

urlpatterns = patterns(
    'home_application.views',
    (r'^$', 'home'),  # 首页
    (r'^dev-guide/$', 'dev_guide'),
    (r'^contactus/$', 'contactus'),
    (r'^search_colony/$', 'search_colony'),  # 查询集群
    (r'^search_pc/$', 'search_pc'),  # 查询主机
    (r'^add_module/$', 'add_module_html'),  # 新增模块的页面

)
