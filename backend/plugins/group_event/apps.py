"""
群体事件应用配置
"""
from django.apps import AppConfig


class GroupEventConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'plugins.group_event'
    verbose_name = '群体事件'
