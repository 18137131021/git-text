# -*- coding: utf-8 -*-
"""
用于测试环境的全局配置
"""
from settings import APP_ID
from conf import default

# ===============================================================================
# 数据库设置, 测试环境数据库设置
# ===============================================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': (default.SITE_URL, 'db.sqlite3'),
    }
}
