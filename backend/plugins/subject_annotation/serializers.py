"""
主体标注序列化器
"""
from rest_framework import serializers
from .models import SubjectTag


class SubjectTagSerializer(serializers.ModelSerializer):
    """主体标注序列化器"""

    class Meta:
        model = SubjectTag
        fields = [
            'id',
            'complaint',
            'subject_name',
            'subject_type',
            'industry',
            'scale',
            'complaint_nature',
            'model',
            'created_at'
        ]
        read_only_fields = ['created_at']
