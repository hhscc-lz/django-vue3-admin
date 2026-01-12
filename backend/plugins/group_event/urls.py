"""
群体事件路由配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GroupEventViewSet, DailySummaryViewSet

router = DefaultRouter()
router.register(r'group-events', GroupEventViewSet, basename='group-event')
router.register(r'daily-summary', DailySummaryViewSet, basename='daily-summary')

urlpatterns = [
    # DRF ViewSet 路由
    path('', include(router.urls)),
]
