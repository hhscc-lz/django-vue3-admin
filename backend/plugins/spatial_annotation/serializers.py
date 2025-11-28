"""
空间标注序列化器
"""
from rest_framework import serializers
from dvadmin.utils.serializers import CustomModelSerializer
from .models import SpatialTag
from plugins.complaint.models import Complaint


class SpatialTagSerializer(CustomModelSerializer):
    """
    空间标注序列化器 (包含工单信息)

    继承 CustomModelSerializer 以获得：
    - 自动时间格式化 (YYYY-MM-DD HH:mm:ss)
    - 中文错误提示
    - 动态字段查询支持
    """
    # 工单ID
    complaint_id = serializers.CharField(source='complaint.id', read_only=True)

    # 嵌套工单信息
    complaint_title = serializers.CharField(source='complaint.title', read_only=True, required=False, allow_null=True, allow_blank=True)
    complaint_region = serializers.CharField(source='complaint.region', read_only=True, required=False, allow_null=True, allow_blank=True)
    complaint_accept_time = serializers.DateTimeField(source='complaint.accept_time', read_only=True, required=False, allow_null=True)
    complaint_status = serializers.CharField(source='complaint.status', read_only=True, required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = SpatialTag
        fields = [
            'id', 'complaint_id', 'address', 'address_type',
            'longitude', 'latitude', 'district', 'street', 'community',
            'created_at',
            # 工单字段
            'complaint_title', 'complaint_region', 'complaint_accept_time',
            'complaint_status'
        ]
        read_only_fields = fields  # 所有字段只读
