"""
主体标注模型
"""
from django.db import models
from plugins.complaint.models import Complaint


class SubjectTag(models.Model):
    """主体标注表"""
    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.DO_NOTHING,
        db_column='complaint_id',
        to_field='id',
        verbose_name='工单编号'
    )
    subject_name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name='被投诉主体名称'
    )
    subject_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='主体类型'
    )
    industry = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='行业类型'
    )
    scale = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='企业规模'
    )
    complaint_nature = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='投诉性质'
    )
    model = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='经营形式'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )

    class Meta:
        db_table = 'subject_tags'
        managed = False
        verbose_name = '主体标注'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.subject_name} ({self.subject_type})'
