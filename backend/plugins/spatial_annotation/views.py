"""
空间标注视图
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import SpatialTag
from .serializers import SpatialTagSerializer
from plugins.complaint.models import Complaint


# ==================== 空间标注浏览API ====================
@api_view(['GET'])
def spatial_annotation_list(request):
    """
    空间标注列表接口

    前端页面: /annotation/spatial
    查询 spatial_tags 表中的记录，联表 complaints 获取工单信息

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

        # 查询空间标注记录，联表 complaints
        queryset = SpatialTag.objects.select_related('complaint').order_by('-created_at')

        # 计算总数
        total = queryset.count()

        # 分页
        start = (page - 1) * size
        end = start + size
        spatial_tags = queryset[start:end]

        # 构建返回数据（左侧列表不显示空间标注信息，模拟"待标注"状态）
        data_list = []
        for spatial_tag in spatial_tags:
            complaint = spatial_tag.complaint
            if complaint:
                data_list.append({
                    'complaint_id': complaint.id,
                    'title': complaint.title or '',
                    'content': complaint.content or '',
                    'accept_time': complaint.accept_time.strftime('%Y-%m-%d %H:%M:%S') if complaint.accept_time else '',
                    'status': complaint.status or '',
                    'region': complaint.region or '',
                    # 左侧列表不显示空间标注信息，保持"待标注"外观
                    # 'address': spatial_tag.address or '',
                    # 'address_type': spatial_tag.address_type or '',
                    # 'annotated_at': spatial_tag.created_at.strftime('%Y-%m-%d %H:%M:%S') if spatial_tag.created_at else ''
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
def spatial_annotation_detail(request, complaint_id):
    """
    空间标注详情接口

    根据 complaint_id 查询空间标注详情和完整工单信息

    参数:
    - complaint_id: 工单编号 (URL路径参数)

    返回:
    {
        "code": 2000,
        "msg": "success",
        "data": {
            "complaint": {...},  # 工单完整信息
            "spatial": {...}     # 空间标注信息
        }
    }
    """
    try:
        # 模拟加载延迟 3秒
        import time
        time.sleep(3)

        # 查询空间标注记录
        spatial_tag = get_object_or_404(
            SpatialTag.objects.select_related('complaint'),
            complaint__id=complaint_id
        )

        complaint = spatial_tag.complaint

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
            'spatial': {
                'address': spatial_tag.address or '',
                'address_type': spatial_tag.address_type or '',
                'longitude': float(spatial_tag.longitude) if spatial_tag.longitude is not None else None,
                'latitude': float(spatial_tag.latitude) if spatial_tag.latitude is not None else None,
                'district': spatial_tag.district or '',
                'street': spatial_tag.street or '',
                'community': spatial_tag.community or '',
                'annotated_at': spatial_tag.created_at.strftime('%Y-%m-%d %H:%M:%S') if spatial_tag.created_at else ''
            }
        }

        return Response({
            'code': 2000,
            'msg': 'success',
            'data': data
        })
    except SpatialTag.DoesNotExist:
        return Response({
            'code': 4004,
            'msg': f'未找到工单 {complaint_id} 的空间标注信息',
            'data': None
        }, status=404)
    except Exception as e:
        return Response({
            'code': 4000,
            'msg': f'查询失败: {str(e)}',
            'data': None
        }, status=500)
