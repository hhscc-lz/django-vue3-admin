"""
风险预警应用配置
"""
from django.apps import AppConfig


class RiskWarningConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'plugins.risk_warning'
    verbose_name = '风险预警'
