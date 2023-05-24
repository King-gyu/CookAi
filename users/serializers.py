from rest_framework import serializers
from rest_framework.exceptions import ParseError, NotAuthenticated
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import User
from articles.models import Article


class FollowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "pk",
            "avatar",
            "nickname",
        )


class MyArticleSerializer(serializers.ModelSerializer):
    userPk = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    createdAt = serializers.SerializerMethodField()

    def get_userPk(self, obj):
        return obj.user.pk

    def get_likes(self, obj):
        return obj.like_users.count()

    def get_comments(self, obj):
        return obj.comments.count()

    def get_createdAt(self, obj):
        return obj.created_at


    class Meta:
        model = Article
        fields = (
            "pk",
            "userPk",
            "title",
            "content",
            "likes",
            "comments",
            "createdAt",
        )


class UserSerializer(serializers.ModelSerializer):
    followings = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()
    article = serializers.SerializerMethodField()

    def get_followings(self, obj):
        followings = obj.following
        serializer = FollowingSerializer(followings, many=True)
        return serializer.data

    def get_followers(self, obj):
        followers = obj.followers
        serializer = FollowingSerializer(followers, many=True)
        return serializer.data

    def get_article(self, obj):
        article = obj.reviews.order_by("-created_at")
        serializer = MyArticleSerializer(article, many=True)
        return serializer.data

    class Meta:
        model = User
        fields = [
            "pk",
            "avatar",
            "email",
            "nickname",
            "intro",
            "followings",
            "followers",
            "article",
        ]

    def update(self, instance, validated_data):
        cur_password = validated_data.pop("password1", None)
        new_password = validated_data.pop("password2", None)

        if not all(cur_password, new_password):
            return ParseError

        if not user.check_password(cur_password):
            raise NotAuthenticated

        user = super().update(instance, validated_data)
        user.set_password(new_password)
        user.save()

        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["nickname"] = user.nickname
        return token