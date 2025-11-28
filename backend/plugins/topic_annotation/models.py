"""
专题标注模型
"""
from django.db import models
from plugins.complaint.models import Complaint


class TopicTag(models.Model):
    """专题标注表"""
    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.DO_NOTHING,
        db_column='complaint_id',
        to_field='id',
        verbose_name='工单编号'
    )
    topic_name = models.CharField(
        max_length=50,
        verbose_name='专题名称'
    )
    topic_fields = models.JSONField(
        null=True,
        blank=True,
        verbose_name='专题细分字段'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )

    class Meta:
        db_table = 'topic_tags'
        managed = False
        verbose_name = '专题标注'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.complaint.id} - {self.topic_name}'
