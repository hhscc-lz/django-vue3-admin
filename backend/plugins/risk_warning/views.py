"""
风险预警视图
"""
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as filters
from openpyxl import Workbook
from django.http import HttpResponse
from datetime import datetime

from .models import RiskTag
from .serializers import RiskTagSerializer, RiskTagExportSerializer
from dvadmin.utils.viewset import CustomModelViewSet


class RiskTagFilter(filters.FilterSet):
    """
    风险标注过滤器 (按工单的受理时间筛选)
    """
    # 按工单受理时间筛选
    accept_time_start = filters.DateTimeFilter(
        field_name='complaint__accept_time',
        lookup_expr='gte',
        label='受理时间开始'
    )
    accept_time_end = filters.DateTimeFilter(
        field_name='complaint__accept_time',
        lookup_expr='lte',
        label='受理时间结束'
    )

    # 按风险类别筛选
    risk_category = filters.CharFilter(
        field_name='risk_category',
        lookup_expr='exact',
        label='风险类别'
    )

    # 按是否风险筛选
    is_risk = filters.BooleanFilter(
        field_name='is_risk',
        label='是否风险'
    )

    # 按工单ID筛选
    complaint_id = filters.CharFilter(
        field_name='complaint_id',
        lookup_expr='exact',
        label='工单编号'
    )


    class Meta:
        model = RiskTag
        fields = [
            'accept_time_start', 'accept_time_end',
            'risk_category', 'is_risk', 'complaint_id'
        ]


class RiskTagViewSet(CustomModelViewSet):
    """
    风险预警视图集 (只读)

    仅提供:
    - list: 列表查询
    - retrieve: 详情查询
    - export_data: 导出Excel (包含工单信息)

    不提供 create/update/delete 功能
    """
    queryset = RiskTag.objects.select_related('complaint').all()
    serializer_class = RiskTagSerializer
    filterset_class = RiskTagFilter
    search_fields = ['complaint__id', 'risk_category', 'risk_reason']
    ordering_fields = ['created_at', 'complaint__accept_time']
    ordering = ['-created_at']

    # 禁用创建、更新、删除操作
    http_method_names = ['get', 'head', 'options']

    def get_queryset(self):
        """
        优化查询: 预加载关联的工单信息
        """
        queryset = super().get_queryset()
        # 使用 select_related 优化外键查询
        return queryset.select_related('complaint')

    @action(methods=['get'], detail=False, url_path='export')
    def export_data(self, request, *args, **kwargs):
        """
        导出风险预警数据 (包含完整工单信息)
        """
        # 获取筛选后的查询集
        queryset = self.filter_queryset(self.get_queryset())

        # 使用导出序列化器
        serializer = RiskTagExportSerializer(queryset, many=True)
        data = serializer.data

        # 创建 Excel 工作簿
        wb = Workbook()
        ws = wb.active
        ws.title = '风险预警数据'

        # 写入表头
        if data:
            headers = list(data[0].keys())
            ws.append(headers)

            # 写入数据
            for item in data:
                row = [item.get(header, '') for header in headers]
                ws.append(row)

        # 设置列宽
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width

        # 生成响应
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        filename = f'风险预警数据_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        wb.save(response)
        return response


    def create(self, request, *args, **kwargs):
        """禁用创建操作"""
        return Response({
            'code': 4000,
            'msg': '风险预警数据为只读，不支持创建操作'
        }, status=403)

    def update(self, request, *args, **kwargs):
        """禁用更新操作"""
        return Response({
            'code': 4000,
            'msg': '风险预警数据为只读，不支持更新操作'
        }, status=403)

    def partial_update(self, request, *args, **kwargs):
        """禁用部分更新操作"""
        return Response({
            'code': 4000,
            'msg': '风险预警数据为只读，不支持更新操作'
        }, status=403)

    def destroy(self, request, *args, **kwargs):
        """禁用删除操作"""
        return Response({
            'code': 4000,
            'msg': '风险预警数据为只读，不支持删除操作'
        }, status=403)
