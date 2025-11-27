"""
风险预警路由配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RiskTagViewSet

router = DefaultRouter()
router.register(r'risk-tags', RiskTagViewSet, basename='risk-tag')

urlpatterns = [
    path('', include(router.urls)),
]
