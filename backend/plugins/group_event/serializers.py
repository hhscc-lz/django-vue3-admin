"""
群体事件序列化器
"""
from rest_framework import serializers
from dvadmin.utils.serializers import CustomModelSerializer
from .models import GroupEvent, GroupEventComplaint, GroupEventDailySummary
from plugins.complaint.models import Complaint


class ComplaintSimpleSerializer(CustomModelSerializer):
    """
    工单简化序列化器 (用于嵌套显示)

    只包含关键字段，减少数据传输量
    """
    class Meta:
        model = Complaint
        fields = [
            'id', 'title', 'region', 'accept_time', 'status',
            'complete_time', 'category_level1', 'category_level2'
        ]
        read_only_fields = fields


class GroupEventSerializer(CustomModelSerializer):
    """
    群体事件列表序列化器

    用于列表展示，包含基本信息和关联工单数量
    """
    # 触发工单的标题（嵌套字段）
    trigger_complaint_title = serializers.SerializerMethodField()

    class Meta:
        model = GroupEvent
        fields = [
            'id', 'title', 'trigger_complaint_id', 'trigger_complaint_title',
            'complaint_count', 'region', 'created_at'
        ]
        read_only_fields = fields

    def get_trigger_complaint_title(self, obj):
        """
        获取触发工单的标题

        使用 try-except 处理工单不存在的情况
        """
        try:
            complaint = Complaint.objects.get(id=obj.trigger_complaint_id)
            return complaint.title
        except Complaint.DoesNotExist:
            return None


class GroupEventDetailSerializer(CustomModelSerializer):
    """
    群体事件详情序列化器

    用于详情查看，包含完整信息和关联工单列表
    """
    # 触发工单信息
    trigger_complaint_title = serializers.SerializerMethodField()

    # 关联工单列表（使用 SerializerMethodField 动态获取）
    related_complaints = serializers.SerializerMethodField()

    class Meta:
        model = GroupEvent
        fields = [
            'id', 'title', 'trigger_complaint_id', 'trigger_complaint_title',
            'complaint_count', 'region', 'created_at',
            'related_complaints'  # 关联工单列表
        ]
        read_only_fields = fields

    def get_trigger_complaint_title(self, obj):
        """获取触发工单标题"""
        try:
            complaint = Complaint.objects.get(id=obj.trigger_complaint_id)
            return complaint.title
        except Complaint.DoesNotExist:
            return None

    def get_related_complaints(self, obj):
        """
        获取所有关联工单列表

        注意：需要在 ViewSet 中使用 prefetch_related 预加载
        避免 N+1 查询问题
        """
        # 通过反向关系获取所有关联的工单
        # obj.event_complaints 是 GroupEventComplaint 的查询集
        event_complaints = obj.event_complaints.select_related('complaint').all()

        # 提取工单对象并序列化
        complaints = [ec.complaint for ec in event_complaints]
        return ComplaintSimpleSerializer(complaints, many=True).data


class GroupEventComplaintSerializer(CustomModelSerializer):
    """
    群体事件关联工单序列化器

    用于关联工单的详细展示（带工单完整信息）
    """
    # 嵌套完整工单信息
    complaint_detail = ComplaintSimpleSerializer(source='complaint', read_only=True)

    # 事件基本信息
    event_title = serializers.CharField(source='group_event.title', read_only=True)

    class Meta:
        model = GroupEventComplaint
        fields = [
            'id', 'group_event_id', 'event_title',
            'complaint_id', 'complaint_detail',
            'created_at'
        ]
        read_only_fields = fields


class DailySummarySerializer(CustomModelSerializer):
    """
    群体事件每日摘要序列化器
    """
    class Meta:
        model = GroupEventDailySummary
        fields = [
            'id', 'summary_date', 'title', 'content',
            'event_count', 'event_ids', 'created_at'
        ]
        read_only_fields = fields
