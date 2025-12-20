"""
群体事件数据模型
映射到已存在的 group_events 和 group_event_complaints 表
"""
from django.db import models
from plugins.complaint.models import Complaint


class GroupEvent(models.Model):
    """
    群体事件表 (只读映射)

    存储 AI 识别的群体性诉求事件
    """
    # 主键
    id = models.AutoField(primary_key=True)

    # 事件信息
    title = models.CharField(max_length=500, verbose_name='事件摘要标题')
    trigger_complaint_id = models.CharField(max_length=50, verbose_name='触发诉求ID')
    complaint_count = models.IntegerField(default=0, verbose_name='关联诉求数量')
    region = models.CharField(max_length=50, null=True, blank=True, verbose_name='主要区域')

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'group_events'
        managed = False  # 重要：不让 Django 管理表结构
        verbose_name = '群体事件'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.id} - {self.title}"


class GroupEventComplaint(models.Model):
    """
    群体事件关联工单表 (只读映射)

    存储事件与诉求的多对多关联关系
    """
    # 主键
    id = models.AutoField(primary_key=True)

    # 关联字段
    group_event = models.ForeignKey(
        GroupEvent,
        on_delete=models.DO_NOTHING,
        db_column='group_event_id',
        related_name='event_complaints',  # 反向查询名称：event.event_complaints.all()
        verbose_name='群体事件'
    )

    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.DO_NOTHING,
        db_column='complaint_id',
        to_field='id',  # Complaint 主键是 CharField，需要显式指定
        related_name='group_events',
        verbose_name='关联工单'
    )

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'group_event_complaints'
        managed = False
        verbose_name = '群体事件关联工单'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"Event {self.group_event_id} - Complaint {self.complaint_id}"
