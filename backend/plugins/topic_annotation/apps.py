"""
专题标注应用配置
"""
from django.apps import AppConfig


class TopicAnnotationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'plugins.topic_annotation'
    verbose_name = '专题标注管理'
