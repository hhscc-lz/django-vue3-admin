"""
风险预警视图
"""
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django_filters import rest_framework as filters
from openpyxl import Workbook
from django.http import HttpResponse
from datetime import datetime
from django.shortcuts import get_object_or_404

from .models import RiskTag
from .serializers import RiskTagSerializer, RiskTagExportSerializer
from dvadmin.utils.viewset import CustomModelViewSet
from plugins.complaint.models import Complaint


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


# ==================== 风险标注浏览API ====================
@api_view(['GET'])
def risk_annotation_list(request):
    """
    风险标注列表接口

    前端页面: /annotation/risk
    查询 risk_tags 表中 is_risk=1 的记录，联表 complaints 获取工单信息

    参数:
    - page: 页码 (默认1)
    - size: 每页条数 (默认10)

    返回:
    {
        "code": 2000,
        "msg": "success",
        "data": {
            "data": [...],  # 数据列表
            "total": 100,   # 总条数
            "page": 1,      # 当前页
            "size": 10      # 每页条数
        }
    }
    """
    try:
        # 模拟加载延迟 3秒
        import time
        time.sleep(3)

        # 获取分页参数
        page = int(request.GET.get('page', 1))
        size = int(request.GET.get('size', 10))

        # 查询 is_risk=1 的记录，联表 complaints
        queryset = RiskTag.objects.filter(is_risk=True).select_related('complaint').order_by('-created_at')

        # 计算总数
        total = queryset.count()

        # 分页
        start = (page - 1) * size
        end = start + size
        risk_tags = queryset[start:end]

        # 构建返回数据（左侧列表不显示风险类别，模拟"待标注"状态）
        data_list = []
        for risk_tag in risk_tags:
            complaint = risk_tag.complaint
            if complaint:
                data_list.append({
                    'complaint_id': complaint.id,
                    'title': complaint.title or '',
                    'content': complaint.content or '',
                    'accept_time': complaint.accept_time.strftime('%Y-%m-%d %H:%M:%S') if complaint.accept_time else '',
                    'status': complaint.status or '',
                    'region': complaint.region or '',
                    # 左侧列表不显示风险类别，保持"待标注"外观
                    # 'is_risk': risk_tag.is_risk,
                    # 'risk_category': risk_tag.risk_category or '',
                    # 'annotated_at': risk_tag.created_at.strftime('%Y-%m-%d %H:%M:%S') if risk_tag.created_at else ''
                })

        return Response({
            'code': 2000,
            'msg': 'success',
            'data': {
                'data': data_list,
                'total': total,
                'page': page,
                'size': size
            }
        })
    except Exception as e:
        return Response({
            'code': 4000,
            'msg': f'查询失败: {str(e)}',
            'data': None
        }, status=500)


@api_view(['GET'])
def risk_annotation_detail(request, complaint_id):
    """
    风险标注详情接口

    根据 complaint_id 查询风险标注详情和完整工单信息

    参数:
    - complaint_id: 工单编号 (URL路径参数)

    返回:
    {
        "code": 2000,
        "msg": "success",
        "data": {
            "complaint": {...},  # 工单完整信息
            "risk": {...}        # 风险标注信息
        }
    }
    """
    try:
        # 模拟加载延迟 3秒
        import time
        time.sleep(3)

        # 查询风险标注记录
        risk_tag = get_object_or_404(
            RiskTag.objects.select_related('complaint'),
            complaint__id=complaint_id,
            is_risk=True
        )

        complaint = risk_tag.complaint

        # 构建返回数据
        data = {
            'complaint': {
                'complaint_id': complaint.id,
                'title': complaint.title or '',
                'content': complaint.content or '',
                'accept_time': complaint.accept_time.strftime('%Y-%m-%d %H:%M:%S') if complaint.accept_time else '',
                'status': complaint.status or '',
                'region': complaint.region or '',
                'complainant_name': complaint.complainant_name or '',
                'complainant_phone': complaint.complainant_phone or '',
                'handle_department': complaint.handle_department or '',
                'source_channel': complaint.source_channel or '',
            },
            'risk': {
                'is_risk': risk_tag.is_risk,
                'risk_category': risk_tag.risk_category or '',
                'risk_reason': risk_tag.risk_reason or '',
                'annotated_at': risk_tag.created_at.strftime('%Y-%m-%d %H:%M:%S') if risk_tag.created_at else ''
            }
        }

        return Response({
            'code': 2000,
            'msg': 'success',
            'data': data
        })
    except RiskTag.DoesNotExist:
        return Response({
            'code': 4004,
            'msg': f'未找到工单 {complaint_id} 的风险标注信息',
            'data': None
        }, status=404)
    except Exception as e:
        return Response({
            'code': 4000,
            'msg': f'查询失败: {str(e)}',
            'data': None
        }, status=500)
