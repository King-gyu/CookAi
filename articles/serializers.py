from django.db import models
from rest_framework import serializers
from articles.models import Article, Comment, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    likes = serializers.StringRelatedField(many=True)

    def get_user(self, obj):
        return obj.user.email

    def get_likes_count(self, obj):
        return obj.likes.count()

    class Meta:
        model = Comment
        fields = '__all__'


class ArticleSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    likes = serializers.StringRelatedField(many=True)
    tags = TagSerializer(many=True)

    def get_user(self, obj):
        return obj.user.email

    def get_likes_count(self, obj):
        return obj.likes.count()

    class Meta:
        model = Article
        fields = '__all__'


class ArticleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ('title', 'content', 'image', 'tags')

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            article = Article(**validated_data)
            article.user = request.user
            article.save()
            return article
        else:
            raise serializers.ValidationError('로그인이 필요합니다.')

class ArticleListSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        return obj.user.email

    class Meta:
        model = Article
        fields = ('pk', 'user', 'title', 'content', 'created_at', 'updated_at')


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('content', 'image')
