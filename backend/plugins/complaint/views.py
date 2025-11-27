"""
工单视图集
"""
from rest_framework.decorators import action
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.json_response import DetailResponse
from .models import Complaint
from .serializers import ComplaintFullDetailSerializer


class ComplaintViewSet(CustomModelViewSet):
    """
    工单视图集

    提供工单的通用查询接口：
    - 详情查询：GET /api/complaint/complaints/{id}/
    - 完整详情：GET /api/complaint/complaints/{id}/full-detail/
    """
    queryset = Complaint.objects.all()
    serializer_class = ComplaintFullDetailSerializer

    @action(methods=['get'], detail=True, url_path='full-detail')
    def full_detail(self, request, pk=None):
        """
        获取完整的工单详情（包含所有关联信息）

        路径：GET /api/complaint/complaints/{id}/full-detail/

        返回：
        - 工单所有字段
        - 关联的风险标注信息
        - 关联的情感分析信息（待实现）

        使用 prefetch_related 优化查询性能
        """
        # 获取工单并预加载关联数据
        complaint = self.get_queryset().prefetch_related('risk_tags').get(pk=pk)

        # 序列化数据
        serializer = self.get_serializer(complaint)

        # 使用 DetailResponse 包装返回数据（符合项目标准响应格式）
        return DetailResponse(data=serializer.data, msg="获取成功")

