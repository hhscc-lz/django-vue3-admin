"""
风险预警模块数据模型
映射到已存在的 complaints 和 risk_tags 表
"""
from django.db import models


class Complaint(models.Model):
    """
    12345 诉求表 (只读映射)
    """
    # 主键
    id = models.CharField(max_length=50, primary_key=True, verbose_name='工单编号')

    # 基础信息
    complainant_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='诉求人姓名')
    complainant_phone = models.CharField(max_length=20, null=True, blank=True, verbose_name='诉求人手机号')

    # 诉求内容
    title = models.CharField(max_length=500, null=True, blank=True, verbose_name='诉求标题')
    content = models.TextField(null=True, blank=True, verbose_name='市民诉求')

    # 分类信息
    category_level1 = models.CharField(max_length=100, null=True, blank=True, verbose_name='接诉分类一级')
    category_level2 = models.CharField(max_length=100, null=True, blank=True, verbose_name='接诉分类二级')
    category_level3 = models.CharField(max_length=100, null=True, blank=True, verbose_name='接诉分类三级')
    category_level4 = models.CharField(max_length=100, null=True, blank=True, verbose_name='接诉分类四级')
    order_type = models.CharField(max_length=50, null=True, blank=True, verbose_name='工单类型')
    complaint_type = models.CharField(max_length=50, null=True, blank=True, verbose_name='诉求类型')
    region = models.CharField(max_length=100, null=True, blank=True, verbose_name='所属区域')

    # 流程信息
    accept_time = models.DateTimeField(null=True, blank=True, verbose_name='受理时间')
    status = models.CharField(max_length=50, null=True, blank=True, verbose_name='工单状态')
    source_channel = models.CharField(max_length=50, null=True, blank=True, verbose_name='来源渠道')
    complete_time = models.DateTimeField(null=True, blank=True, verbose_name='提交办结时间')
    reply_time = models.DateTimeField(null=True, blank=True, verbose_name='回复时间')
    reply_person = models.TextField(null=True, blank=True, verbose_name='回复诉求人')
    callback_result = models.CharField(max_length=200, null=True, blank=True, verbose_name='回访结果')
    handle_department = models.CharField(max_length=200, null=True, blank=True, verbose_name='处理部门')

    # 统计信息
    urge_count = models.IntegerField(null=True, blank=True, verbose_name='催单次数')
    supplement_count = models.IntegerField(null=True, blank=True, verbose_name='补单次数')
    repeat_count = models.IntegerField(null=True, blank=True, verbose_name='重复次数')

    class Meta:
        db_table = 'complaints'
        managed = False
        verbose_name = '12345诉求'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.id} - {self.title}"


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
