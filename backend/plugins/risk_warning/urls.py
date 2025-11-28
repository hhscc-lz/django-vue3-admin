"""
风险预警路由配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RiskTagViewSet, risk_annotation_list, risk_annotation_detail

router = DefaultRouter()
router.register(r'risk-tags', RiskTagViewSet, basename='risk-tag')

urlpatterns = [
    # DRF ViewSet 路由 (用于管理后台)
    path('', include(router.urls)),

    # 风险标注浏览 API (用于前端页面)
    path('annotation/risk/list', risk_annotation_list, name='risk-annotation-list'),
    path('annotation/risk/detail/<str:complaint_id>', risk_annotation_detail, name='risk-annotation-detail'),
]
