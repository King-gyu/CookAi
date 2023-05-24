import os
import requests

from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework import status, permissions
from rest_framework.response import Response

from users.serializers import (
    UserSerializer,
    CustomTokenObtainPairSerializer,
    FollowingSerializer,
)
from users.models import User


class UserList(APIView):
    def get(self, request):
        user = User.objects.all()
        serializer = UserSerializer(user, many=True)
        return Response(serializer.data)


class Me(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if user:
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class UserView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        if request.user == user:
            serializer = UserSerializer(user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        if request.user == user:
            user.is_active = False
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class FollowView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        you = get_object_or_404(User, id=user_id)
        me = request.user
        is_follow = request.data.get("is_follow")

        if is_follow:
            you.followers.add(me)
        else:
            you.followers.remove(me)

        serializer = FollowingSerializer(me.following, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class KaKaoLogin(APIView):
    def post(self, request):
        code = request.data.get("code", None)
        token_url = f"https://kauth.kakao.com/oauth/token"
        redirect_uri = "http://127.0.0.1:3000/social/kakao"

        if code is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        response = requests.post(
            token_url,
            data={
                "grant_type": "authorization_code",
                "client_id": os.environ.get("KAKAO_API_KEY"),
                "redirect_uri": redirect_uri,
                "code": code,
                "client_secret": os.environ.get("KAKAO_CLIENT_SECRET"),
            },
            headers={"Content-type": "application/x-www-form-urlencoded;charset=utf-8"},
        )

        access_token = response.json().get("access_token")
        user_url = "https://kapi.kakao.com/v2/user/me"
        response = requests.get(
            user_url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
            },
        )
        user_data = response.json()
        kakao_account = user_data.get("kakao_account")
        profile = kakao_account.get("profile")

        if not kakao_account.get("is_email_valid") and not kakao_account.get(
            "is_email_verified"
        ):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        user_email = kakao_account.get("email")

        try:
            user = User.objects.get(email=user_email)
            refresh_token = CustomTokenObtainPairSerializer.get_token(user)

            return Response(
                {
                    "refresh": str(refresh_token),
                    "access": str(refresh_token.access_token),
                }
            )

        except User.DoesNotExist:
            user = User.objects.create_user(email=user_email)
            user.set_unusable_password()
            user.nickname = profile.get("nickname", f"user#{user.pk}")
            user.avatar = profile.get("thumbnail_image_url", None)
            user.save()

            refresh_token = CustomTokenObtainPairSerializer.get_token(user)

            return Response(
                {
                    "refresh": str(refresh_token),
                    "access": str(refresh_token.access_token),
                }
            )


class GithubLogin(APIView):
    def post(self, request):
        code = request.data.get("code", None)
        token_url = "https://github.com/login/oauth/access_token"
        redirect_uri = "http://127.0.0.1:3000/social/github"

        if code is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        response = requests.post(
            token_url,
            data={
                "client_id": os.environ.get("GH_CLIENT_ID"),
                "client_secret": os.environ.get("GH_CLIENT_SECRET"),
                "code": code,
                "redirect_uri": redirect_uri,
            },
            headers={
                "Accept": "application/json",
            },
        )

        access_token = response.json().get("access_token")
        user_url = "https://api.github.com/user"
        user_email_url = "https://api.github.com/user/emails"

        response = requests.get(
            user_url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            },
        )

        user_data = response.json()

        response = requests.get(
            user_email_url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            },
        )

        user_emails = response.json()

        user_email = None

        for email_data in user_emails:
            if email_data.get("primary") and email_data.get("verified"):
                user_email = email_data.get("email")

        try:
            user = User.objects.get(email=user_email)
            refresh_token = CustomTokenObtainPairSerializer.get_token(user)

            return Response(
                {
                    "refresh": str(refresh_token),
                    "access": str(refresh_token.access_token),
                }
            )

        except User.DoesNotExist:
            user = User.objects.create_user(email=user_email)
            user.set_unusable_password()
            user.nickname = user_data.get("login", f"user#{user.pk}")
            user.avatar = user_data.get("avatar_url", None)
            user.save()

            refresh_token = CustomTokenObtainPairSerializer.get_token(user)

            return Response(
                {
                    "refresh": str(refresh_token),
                    "access": str(refresh_token.access_token),
                }
            )