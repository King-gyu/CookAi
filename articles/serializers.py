# 게시글 작성, 수정, 삭제, 조회를 위한 serializer

from rest_framework import serializers
from articles.models import Article, Comment

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'
        
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

        