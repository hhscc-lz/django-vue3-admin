"""
空间标注插件配置
"""
from django.apps import AppConfig


class SpatialAnnotationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'plugins.spatial_annotation'
    verbose_name = '空间标注'
