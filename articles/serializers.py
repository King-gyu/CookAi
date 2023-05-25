# 게시글 작성, 수정, 삭제, 조회를 위한 serializer

from rest_framework import serializers
from .models import Article, Comment

class ArticleSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    class Meta:
        model = Article
        fields = '__all__'
        
class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    comments = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta:
        model = Comment
        fields = '__all__'

        