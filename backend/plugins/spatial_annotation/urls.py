"""
空间标注路由配置
"""
from django.urls import path
from .views import spatial_annotation_list, spatial_annotation_detail

urlpatterns = [
    # 空间标注浏览 API (用于前端页面)
    path('annotation/spatial/list', spatial_annotation_list, name='spatial-annotation-list'),
    path('annotation/spatial/detail/<str:complaint_id>', spatial_annotation_detail, name='spatial-annotation-detail'),
]
