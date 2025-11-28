"""
空间标注模块数据模型
映射到已存在的 spatial_tags 表
"""
from django.db import models
from plugins.complaint.models import Complaint


class SpatialTag(models.Model):
    """
    空间标注表 (只读映射)
    """
    # 主键
    id = models.AutoField(primary_key=True)

    # 关联工单 (使用 to_field 映射到 Complaint.id)
    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.DO_NOTHING,
        db_column='complaint_id',
        to_field='id',
        related_name='spatial_tags',
        verbose_name='工单'
    )

    # 地址信息
    address = models.CharField(max_length=500, null=True, blank=True, verbose_name='提取的诉求地址')
    address_type = models.CharField(max_length=50, null=True, blank=True, verbose_name='地址类型')

    # 坐标信息
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True, verbose_name='经度')
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True, verbose_name='纬度')

    # 定位信息
    district = models.CharField(max_length=100, null=True, blank=True, verbose_name='区县')
    street = models.CharField(max_length=100, null=True, blank=True, verbose_name='街道')
    community = models.CharField(max_length=200, null=True, blank=True, verbose_name='小区')

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'spatial_tags'
        managed = False
        verbose_name = '空间标注'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.complaint_id} - {self.address}"

    @property
    def complaint_id(self):
        """兼容属性：返回工单ID"""
        return self.complaint.id if self.complaint else None
