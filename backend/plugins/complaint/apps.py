from django.apps import AppConfig


class ComplaintConfig(AppConfig):
    """工单应用配置"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'plugins.complaint'
    verbose_name = '工单管理'
