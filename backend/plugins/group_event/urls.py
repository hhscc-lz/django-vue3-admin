"""
群体事件路由配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GroupEventViewSet

router = DefaultRouter()
router.register(r'group-events', GroupEventViewSet, basename='group-event')

urlpatterns = [
    # DRF ViewSet 路由
    path('', include(router.urls)),
]
