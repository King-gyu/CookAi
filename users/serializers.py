from rest_framework import serializers, exceptions
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.models import User
from articles.serializers import ArticleSerializer

from base64 import urlsafe_b64encode
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import smart_bytes, force_str
from django.contrib.auth import authenticate
from django.db.models.query_utils import Q
from django.core.mail import EmailMessage
import threading

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ["followings",]

    def create(self, validated_data):
        user = super().create(validated_data)
        password = user.password
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        user = super().update(instance, validated_data)
        password = user.password
        user.set_password(password)
        user.save()
        return user
    
class UserProfileSerializer(serializers.ModelSerializer):
    followings = serializers.StringRelatedField(many=True)
    followers = serializers.StringRelatedField(many=True)
    
    class Meta:
        model = User
        fields = ("email", "name", "followings", "followers")

class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()

class Util:
    @staticmethod
    def send_email(message):
        email = EmailMessage(subject=message["email_subject"], 
                             body=message["email_body"], 
                             to=[message["to_email"]])
        EmailThread(email).start()


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    class Meta:
        fields = ("email",)

    def validate(self, attrs):
        try:
            email = attrs.get("email")

            user = User.objects.get(email=email)
            uidb64 = urlsafe_b64encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)

            frontend_site = "http://127.0.0.1:8000"
            #frontend_site = "127.0.0.1:5500"
            absurl = f"http://{frontend_site}/set_password.html?id=${uidb64}&token=${token}"

            email_body = "비밀번호 재설정 \n " + absurl
            message = {
                "email_body": email_body,
                "to_email": user.email,
                "email_subject": "비밀번호 재설정",
            }
            Util.send_email(message)

            return super().validate(attrs)

        except User.DoesNotExist:
            raise serializers.ValidationError(
                detail={"email": "잘못된 이메일입니다. 다시 입력해주세요."})


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        write_only=True,
    )
    repassword = serializers.CharField(
        write_only=True,
    )
    token = serializers.CharField(
        max_length=100,
        write_only=True,
    )
    uidb64 = serializers.CharField(
        max_length=100,
        write_only=True,
    )

    class Meta:
        fields = (
            "repassword",
            "password",
            "token",
            "uidb64",
        )

    def validate(self, attrs):
        password = attrs.get("password")
        repassword = attrs.get("repassword")
        token = attrs.get("token")
        uidb64 = attrs.get("uidb64")

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=user_id)

            if PasswordResetTokenGenerator().check_token(user, token) == False:
                raise exceptions.AuthenticationFailed("토큰이 유효하지 않습니다.", 401)
            if password != repassword:
                raise serializers.ValidationError(
                    detail={"repassword": "비밀번호가 일치하지 않습니다."})

            user.set_password(password)
            user.save()

            return super().validate(attrs)

        except User.DoesNotExist:
            raise serializers.ValidationError(
                detail={"user": "존재하지 않는 회원입니다."})


class TokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
    )

class PasswordVerificationSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=128)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["name"] = user.name
        return token