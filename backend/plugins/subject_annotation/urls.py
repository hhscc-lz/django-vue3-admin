"""
主体标注路由配置
"""
from django.urls import path
from .views import subject_annotation_list, subject_annotation_detail

urlpatterns = [
    # 主体标注浏览 API (用于前端页面)
    path('annotation/subject/list', subject_annotation_list, name='subject-annotation-list'),
    path('annotation/subject/detail/<str:complaint_id>', subject_annotation_detail, name='subject-annotation-detail'),
]
