"""
群体事件视图
"""
from django.db.models import Prefetch
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as filters

from .models import GroupEvent, GroupEventComplaint, GroupEventDailySummary
from .serializers import (
    GroupEventSerializer,
    GroupEventDetailSerializer,
    GroupEventComplaintSerializer,
    DailySummarySerializer,
)
from dvadmin.utils.viewset import CustomModelViewSet


class GroupEventFilter(filters.FilterSet):
    """
    群体事件过滤器
    """
    # 按创建时间范围筛选
    created_at_start = filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        label='创建时间开始'
    )
    created_at_end = filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        label='创建时间结束'
    )

    # 按区域筛选
    region = filters.CharFilter(
        field_name='region',
        lookup_expr='icontains',  # 模糊匹配
        label='区域'
    )

    # 按标题搜索
    title = filters.CharFilter(
        field_name='title',
        lookup_expr='icontains',
        label='事件标题'
    )

    class Meta:
        model = GroupEvent
        fields = ['created_at_start', 'created_at_end', 'region', 'title']


class GroupEventViewSet(CustomModelViewSet):
    """
    群体事件视图集 (只读)

    提供功能：
    - list: 列表查询
    - retrieve: 详情查询（包含关联工单）
    - related_complaints: 获取某事件的关联工单（分页）

    不提供 create/update/delete 功能
    """
    queryset = GroupEvent.objects.all()
    serializer_class = GroupEventSerializer
    filterset_class = GroupEventFilter
    search_fields = ['title', 'region']  # 支持全文搜索
    ordering_fields = ['created_at', 'complaint_count']
    ordering = ['-created_at']

    # 禁用创建、更新、删除操作
    http_method_names = ['get', 'head', 'options']

    def get_queryset(self):
        """
        优化查询：预加载关联数据
        """
        queryset = super().get_queryset()

        # 根据 action 选择性预加载
        if self.action == 'retrieve':
            # 详情页需要预加载关联工单
            queryset = queryset.prefetch_related(
                Prefetch(
                    'event_complaints',
                    queryset=GroupEventComplaint.objects.select_related('complaint')
                )
            )

        return queryset

    def get_serializer_class(self):
        """
        根据 action 返回不同的序列化器
        """
        if self.action == 'retrieve':
            return GroupEventDetailSerializer
        return GroupEventSerializer

    @action(methods=['get'], detail=True, url_path='related-complaints')
    def related_complaints(self, request, pk=None):
        """
        获取某个事件的关联工单列表（分页）

        URL: /api/group_event/group-events/{id}/related-complaints/

        参数:
        - page: 页码
        - limit: 每页数量

        返回: 分页的工单列表
        """
        # 获取事件对象
        group_event = self.get_object()

        # 获取分页参数
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 20))

        # 查询关联工单（优化：使用 select_related）
        event_complaints = GroupEventComplaint.objects.filter(
            group_event_id=pk
        ).select_related('complaint').order_by('-created_at')

        # 计算总数
        total = event_complaints.count()

        # 分页
        start = (page - 1) * limit
        end = start + limit
        paginated_complaints = event_complaints[start:end]

        # 序列化
        serializer = GroupEventComplaintSerializer(paginated_complaints, many=True)

        # 返回分页响应（兼容 Fast-CRUD 格式）
        return Response({
            'code': 2000,
            'msg': 'success',
            'data': serializer.data,
            'total': total,
            'page': page,
            'limit': limit
        })

    # ========== 禁用的操作 ==========

    def create(self, request, *args, **kwargs):
        """禁用创建操作"""
        return Response({
            'code': 4000,
            'msg': '群体事件数据为只读，不支持创建操作'
        }, status=403)

    def update(self, request, *args, **kwargs):
        """禁用更新操作"""
        return Response({
            'code': 4000,
            'msg': '群体事件数据为只读，不支持更新操作'
        }, status=403)

    def partial_update(self, request, *args, **kwargs):
        """禁用部分更新操作"""
        return Response({
            'code': 4000,
            'msg': '群体事件数据为只读，不支持更新操作'
        }, status=403)

    def destroy(self, request, *args, **kwargs):
        """禁用删除操作"""
        return Response({
            'code': 4000,
            'msg': '群体事件数据为只读，不支持删除操作'
        }, status=403)


class DailySummaryFilter(filters.FilterSet):
    """
    每日摘要过滤器
    """
    # 精确匹配日期
    summary_date = filters.DateFilter(
        field_name='summary_date',
        lookup_expr='exact',
        label='摘要日期'
    )
    # 日期范围
    summary_date_start = filters.DateFilter(
        field_name='summary_date',
        lookup_expr='gte',
        label='摘要日期开始'
    )
    summary_date_end = filters.DateFilter(
        field_name='summary_date',
        lookup_expr='lte',
        label='摘要日期结束'
    )

    class Meta:
        model = GroupEventDailySummary
        fields = ['summary_date', 'summary_date_start', 'summary_date_end']


class DailySummaryViewSet(CustomModelViewSet):
    """
    群体事件每日摘要视图集 (只读)

    提供功能：
    - list: 列表查询（分页）
    - retrieve_by_date: 按日期获取摘要
    """
    queryset = GroupEventDailySummary.objects.all()
    serializer_class = DailySummarySerializer
    filterset_class = DailySummaryFilter
    ordering_fields = ['summary_date', 'event_count']
    ordering = ['-summary_date']

    # 禁用创建、更新、删除操作
    http_method_names = ['get', 'head', 'options']

    @action(methods=['get'], detail=False, url_path='list')
    def list_summaries(self, request):
        """
        获取摘要列表（分页）

        URL: /api/group_event/daily-summary/list
        """
        queryset = self.filter_queryset(self.get_queryset())

        # 分页参数
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 20))

        total = queryset.count()
        start = (page - 1) * limit
        end = start + limit
        paginated = queryset[start:end]

        serializer = self.get_serializer(paginated, many=True)

        return Response({
            'code': 2000,
            'msg': 'success',
            'data': serializer.data,
            'total': total,
            'page': page,
            'limit': limit
        })

    @action(methods=['get'], detail=False, url_path=r'(?P<date>\d{4}-\d{2}-\d{2})')
    def retrieve_by_date(self, request, date=None):
        """
        按日期获取摘要

        URL: /api/group_event/daily-summary/{date}
        """
        try:
            summary = GroupEventDailySummary.objects.get(summary_date=date)
            serializer = self.get_serializer(summary)
            return Response({
                'code': 2000,
                'msg': 'success',
                'data': serializer.data
            })
        except GroupEventDailySummary.DoesNotExist:
            return Response({
                'code': 4000,
                'msg': f'未找到 {date} 的摘要数据'
            }, status=404)
