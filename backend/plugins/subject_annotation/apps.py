"""
主体标注应用配置
"""
from django.apps import AppConfig


class SubjectAnnotationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'plugins.subject_annotation'
    verbose_name = '主体标注管理'
