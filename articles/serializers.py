# 게시글 작성, 수정, 삭제, 조회를 위한 serializer

from rest_framework import serializers
from articles.models import Article, Comment, Tag

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class ArticleSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)

    def get_user(self, obj):
        return obj.user.email
    class Meta:
        model = Article
        fields = '__all__'
        
class ArticleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ('title', 'content', 'image')
        
class ArticleListSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    
    def get_user(self, obj):
        return obj.user.email
    
    class Meta:
        model = Article
        fields = ('pk', 'title', 'content', 'created_at', 'updated_at')
        
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
        
class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('content', 'image')

        