"""
专题标注序列化器
"""
from rest_framework import serializers
from .models import TopicTag


class TopicTagSerializer(serializers.ModelSerializer):
    """专题标注序列化器"""

    class Meta:
        model = TopicTag
        fields = [
            'id',
            'complaint',
            'topic_name',
            'topic_fields',
            'created_at'
        ]
        read_only_fields = ['created_at']
