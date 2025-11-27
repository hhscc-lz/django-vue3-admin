"""
工单序列化器
"""
from rest_framework import serializers
from dvadmin.utils.serializers import CustomModelSerializer
from .models import Complaint


class ComplaintSimpleSerializer(CustomModelSerializer):
    """
    工单简化序列化器 (用于嵌套显示)

    仅包含工单的基本字段，适合在列表或嵌套场景中使用
    """
    class Meta:
        model = Complaint
        fields = [
            'id', 'title', 'region', 'accept_time', 'status',
            'complete_time', 'category_level1', 'category_level2'
        ]
        read_only_fields = fields


class RiskInfoSerializer(serializers.Serializer):
    """
    风险信息嵌套序列化器 (用于工单详情中显示风险标注)

    使用 Serializer 而非 ModelSerializer，避免循环依赖
    由调用方传入已序列化的风险信息数据
    """
    id = serializers.IntegerField(read_only=True)
    is_risk = serializers.BooleanField(read_only=True)
    risk_category = serializers.CharField(read_only=True, allow_null=True, allow_blank=True)
    risk_reason = serializers.CharField(read_only=True, allow_null=True, allow_blank=True)
    created_at = serializers.DateTimeField(read_only=True, allow_null=True)


class ComplaintFullDetailSerializer(CustomModelSerializer):
    """
    工单完整详情序列化器

    用于工单详情弹窗展示，包含：
    - 所有工单字段
    - 关联的风险标注信息（如果有）

    继承 CustomModelSerializer 以获得：
    - 自动时间格式化 (YYYY-MM-DD HH:mm:ss)
    - 中文错误提示
    - 动态字段查询支持
    """
    # 嵌套风险标注信息（使用 SerializerMethodField 动态获取）
    risk_info = serializers.SerializerMethodField()

    class Meta:
        model = Complaint
        fields = [
            # 主键
            'id',

            # 基础信息
            'complainant_name', 'complainant_phone',

            # 诉求内容
            'title', 'content',

            # 分类信息
            'category_level1', 'category_level2', 'category_level3', 'category_level4',
            'order_type', 'complaint_type', 'region',

            # 流程信息
            'accept_time', 'status', 'source_channel',
            'complete_time', 'reply_time', 'reply_person',
            'callback_result', 'handle_department',

            # 统计信息
            'urge_count', 'supplement_count', 'repeat_count',

            # 关联信息
            'risk_info'
        ]
        read_only_fields = fields

    def get_risk_info(self, obj):
        """
        获取关联的风险标注信息

        返回第一条风险标注记录（通常一个工单只有一条风险标注）
        如果没有风险标注，返回 None

        注意：需要在调用时使用 prefetch_related('risk_tags') 优化查询
        """
        # 使用 related_name='risk_tags' 访问反向关联
        risk_tag = obj.risk_tags.first()
        if risk_tag:
            return {
                'id': risk_tag.id,
                'is_risk': risk_tag.is_risk,
                'risk_category': risk_tag.risk_category,
                'risk_reason': risk_tag.risk_reason,
                'created_at': risk_tag.created_at
            }
        return None
