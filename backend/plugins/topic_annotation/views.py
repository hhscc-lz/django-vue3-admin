"""
专题标注视图
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import TopicTag
from .serializers import TopicTagSerializer
from plugins.complaint.models import Complaint


# ==================== 专题标注浏览API ====================
@api_view(['GET'])
def topic_annotation_list(request):
    """
    专题标注列表接口

    前端页面: /annotation/topic
    查询 topic_tags 表中的记录，联表 complaints 获取工单信息

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

        # 查询专题标注记录，联表 complaints，过滤专题名称不为null的记录
        queryset = TopicTag.objects.filter(
            topic_name__isnull=False
        ).exclude(
            topic_name=''
        ).select_related('complaint').order_by('-created_at')

        # 计算总数
        total = queryset.count()

        # 分页
        start = (page - 1) * size
        end = start + size
        topic_tags = queryset[start:end]

        # 构建返回数据（左侧列表不显示专题标注信息，模拟"待标注"状态）
        data_list = []
        for topic_tag in topic_tags:
            complaint = topic_tag.complaint
            if complaint:
                data_list.append({
                    'complaint_id': complaint.id,
                    'title': complaint.title or '',
                    'content': complaint.content or '',
                    'accept_time': complaint.accept_time.strftime('%Y-%m-%d %H:%M:%S') if complaint.accept_time else '',
                    'status': complaint.status or '',
                    'region': complaint.region or '',
                    # 左侧列表不显示专题标注信息，保持"待标注"外观
                    # 'topic_name': topic_tag.topic_name or '',
                    # 'annotated_at': topic_tag.created_at.strftime('%Y-%m-%d %H:%M:%S') if topic_tag.created_at else ''
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
def topic_annotation_detail(request, complaint_id):
    """
    专题标注详情接口

    根据 complaint_id 查询专题标注详情和完整工单信息

    参数:
    - complaint_id: 工单编号 (URL路径参数)

    返回:
    {
        "code": 2000,
        "msg": "success",
        "data": {
            "complaint": {...},  # 工单完整信息
            "topic": {...}       # 专题标注信息
        }
    }
    """
    try:
        # 模拟加载延迟 3秒
        import time
        time.sleep(3)

        # 查询专题标注记录
        topic_tag = get_object_or_404(
            TopicTag.objects.select_related('complaint'),
            complaint__id=complaint_id
        )

        complaint = topic_tag.complaint

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
            'topic': {
                'topic_name': topic_tag.topic_name or '',
                'topic_fields': topic_tag.topic_fields or {},
                'annotated_at': topic_tag.created_at.strftime('%Y-%m-%d %H:%M:%S') if topic_tag.created_at else ''
            }
        }

        return Response({
            'code': 2000,
            'msg': 'success',
            'data': data
        })
    except TopicTag.DoesNotExist:
        return Response({
            'code': 4004,
            'msg': f'未找到工单 {complaint_id} 的专题标注信息',
            'data': None
        }, status=404)
    except Exception as e:
        return Response({
            'code': 4000,
            'msg': f'查询失败: {str(e)}',
            'data': None
        }, status=500)
