"""
专题标注路由配置
"""
from django.urls import path
from .views import topic_annotation_list, topic_annotation_detail

urlpatterns = [
    # 专题标注浏览 API (用于前端页面)
    path('annotation/topic/list', topic_annotation_list, name='topic-annotation-list'),
    path('annotation/topic/detail/<str:complaint_id>', topic_annotation_detail, name='topic-annotation-detail'),
]
