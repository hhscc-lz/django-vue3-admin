"""
风险预警模块数据模型
映射到已存在的 risk_tags 表
"""
from django.db import models
from plugins.complaint.models import Complaint


class RiskTag(models.Model):
    """
    风险标注表 (只读映射)
    """
    # 主键
    id = models.AutoField(primary_key=True)

    # 关联工单 (使用 to_field 映射到 Complaint.id)
    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.DO_NOTHING,
        db_column='complaint_id',
        to_field='id',
        related_name='risk_tags',
        verbose_name='工单'
    )

    # 风险标注
    is_risk = models.BooleanField(default=False, verbose_name='是否存在风险')
    risk_category = models.CharField(max_length=50, null=True, blank=True, verbose_name='风险类别')
    risk_reason = models.TextField(null=True, blank=True, verbose_name='判定原因')

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'risk_tags'
        managed = False
        verbose_name = '风险标注'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.complaint_id} - {self.risk_category}"

    @property
    def complaint_id(self):
        """兼容属性：返回工单ID"""
        return self.complaint.id if self.complaint else None
