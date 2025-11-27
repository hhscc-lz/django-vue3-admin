"""
风险预警序列化器
"""
from rest_framework import serializers
from dvadmin.utils.serializers import CustomModelSerializer
from .models import RiskTag, Complaint


class ComplaintSimpleSerializer(serializers.ModelSerializer):
    """
    工单简化序列化器 (嵌套使用)
    """
    class Meta:
        model = Complaint
        fields = [
            'id', 'title', 'region', 'accept_time', 'status',
            'complete_time', 'category_level1', 'category_level2'
        ]


class RiskTagSerializer(CustomModelSerializer):
    """
    风险标注序列化器 (包含工单信息)

    继承 CustomModelSerializer 以获得：
    - 自动时间格式化 (YYYY-MM-DD HH:mm:ss)
    - 中文错误提示
    - 动态字段查询支持
    """
    # 工单ID
    complaint_id = serializers.CharField(source='complaint.id', read_only=True)

    # 嵌套工单信息 (允许为空)
    complaint_title = serializers.CharField(source='complaint.title', read_only=True, required=False, allow_null=True, allow_blank=True)
    complaint_region = serializers.CharField(source='complaint.region', read_only=True, required=False, allow_null=True, allow_blank=True)
    complaint_accept_time = serializers.DateTimeField(source='complaint.accept_time', read_only=True, required=False, allow_null=True)
    complaint_status = serializers.CharField(source='complaint.status', read_only=True, required=False, allow_null=True, allow_blank=True)
    complaint_complete_time = serializers.DateTimeField(source='complaint.complete_time', read_only=True, required=False, allow_null=True)
    complaint_category_level1 = serializers.CharField(source='complaint.category_level1', read_only=True, required=False, allow_null=True, allow_blank=True)
    complaint_category_level2 = serializers.CharField(source='complaint.category_level2', read_only=True, required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = RiskTag
        fields = [
            'id', 'complaint_id', 'is_risk', 'risk_category', 'risk_reason',
            'created_at',
            # 工单字段
            'complaint_title', 'complaint_region', 'complaint_accept_time',
            'complaint_status', 'complaint_complete_time',
            'complaint_category_level1', 'complaint_category_level2'
        ]
        read_only_fields = fields  # 所有字段只读


class RiskTagExportSerializer(CustomModelSerializer):
    """
    风险标注导出序列化器 (包含完整工单信息用于导出)

    用于 Excel 导出，字段名使用中文
    """
    工单编号 = serializers.CharField(source='complaint.id', required=False, allow_null=True, allow_blank=True)
    是否风险 = serializers.SerializerMethodField()
    风险类别 = serializers.CharField(source='risk_category', required=False, allow_null=True, allow_blank=True)
    判定原因 = serializers.CharField(source='risk_reason', required=False, allow_null=True, allow_blank=True)

    # 工单信息
    诉求标题 = serializers.CharField(source='complaint.title', required=False, allow_null=True, allow_blank=True)
    所属区域 = serializers.CharField(source='complaint.region', required=False, allow_null=True, allow_blank=True)
    受理时间 = serializers.SerializerMethodField()
    工单状态 = serializers.CharField(source='complaint.status', required=False, allow_null=True, allow_blank=True)
    办结时间 = serializers.SerializerMethodField()
    一级分类 = serializers.CharField(source='complaint.category_level1', required=False, allow_null=True, allow_blank=True)
    二级分类 = serializers.CharField(source='complaint.category_level2', required=False, allow_null=True, allow_blank=True)
    三级分类 = serializers.CharField(source='complaint.category_level3', required=False, allow_null=True, allow_blank=True)
    四级分类 = serializers.CharField(source='complaint.category_level4', required=False, allow_null=True, allow_blank=True)
    诉求内容 = serializers.CharField(source='complaint.content', required=False, allow_null=True, allow_blank=True)
    处理部门 = serializers.CharField(source='complaint.handle_department', required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = RiskTag
        fields = [
            '工单编号', '是否风险', '风险类别', '判定原因',
            '诉求标题', '所属区域', '受理时间', '工单状态', '办结时间',
            '一级分类', '二级分类', '三级分类', '四级分类', '诉求内容', '处理部门'
        ]

    def get_是否风险(self, obj):
        return '是' if obj.is_risk else '否'

    def get_受理时间(self, obj):
        if obj.complaint and obj.complaint.accept_time:
            return obj.complaint.accept_time.strftime('%Y-%m-%d %H:%M:%S')
        return ''

    def get_办结时间(self, obj):
        if obj.complaint and obj.complaint.complete_time:
            return obj.complaint.complete_time.strftime('%Y-%m-%d %H:%M:%S')
        return ''
