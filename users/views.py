from base64 import urlsafe_b64decode, urlsafe_b64encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import authenticate
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import DjangoUnicodeDecodeError, force_str, force_bytes
from django.db.models.query_utils import Q
from django.shortcuts import redirect
from django.core.mail import EmailMessage

from rest_framework.authtoken.models import Token
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.generics import CreateAPIView
from rest_framework.parsers import MultiPartParser, FormParser

from users.serializers import UserSerializer, CustomTokenObtainPairSerializer, UserProfileSerializer
from .serializers import PasswordResetSerializer, SetNewPasswordSerializer, TokenSerializer, EmailThread, PasswordVerificationSerializer
from .models import User


class Util:
    @staticmethod
    def send_email(message):
        email = EmailMessage(subject=message["email_subject"], body=message["email_body"], to=[
                             message["to_email"]])
        EmailThread(email).start()


class SignupView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_active = False
            user = serializer.save()

            uid = urlsafe_b64encode(force_bytes(user.pk))
            token = PasswordResetTokenGenerator().make_token(user)

            email = user.email
            authurl = f'http://127.0.0.1:8000/users/verify-email/{uid}/{token}/'
            email_body = "이메일 인증" + authurl
            message = {
                "email_body": email_body,
                "to_email": email,
                "email_subject": "이메일 인증",
            }
            Util.send_email(message)
            return Response({"message": "가입완료!"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": f"${serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        token_generator = PasswordResetTokenGenerator()
        if user is not None and token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return redirect ('http://127.0.0.1:8000/login.html')
            #return redirect ('http://127.0.0.1:5500/login.html')
        else:
            return Response({"message": "잘못된 링크입니다."}, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class ProfileView(APIView):
    def get_object(self, user_id):
        return get_object_or_404(User, id=user_id)

    def get(self, request, user_id):
        user = self.get_object(user_id)
        serializer = UserProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, user_id):
        user = self.get_object(user_id)
        if user == request.user:
            serializer = UserProfileSerializer(
                user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "수정완료!"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "권한이 없습니다!"}, status=status.HTTP_403_FORBIDDEN)

class UserDeleteView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = PasswordVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        password = serializer.validated_data['password']

        if user.check_password(password):
            user.delete()
            return Response({'message': '탈퇴가 성공적으로 처리되었습니다.'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': '비밀번호가 일치하지 않습니다.'}, status=status.HTTP_400_BAD_REQUEST)


class FollowView(APIView):
    def get(self, request, user_id):
        you = get_object_or_404(User, id=user_id)
        serializer = UserProfileSerializer(you)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, user_id):
        you = get_object_or_404(User, id=user_id)
        me = request.user
        if me.is_authenticated:
            if you != request.user:
                if me in you.followers.all():
                    you.followers.remove(me)
                    return Response("unfollow했습니다.", status=status.HTTP_200_OK)
                else:
                    you.followers.add(me)
                    return Response("follow했습니다.", status=status.HTTP_200_OK)
            else:
                return Response("자신을 팔로우 할 수 없습니다.", status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("로그인이 필요합니다.", status=status.HTTP_403_FORBIDDEN)


class PasswordResetView(APIView):
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"message": "비밀번호 재설정 이메일"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordTokenCheckView(APIView):
    def get(self, request, uidb64, token):
        try:
            user_id = force_str(urlsafe_b64decode(uidb64))
            user = get_object_or_404(User, id=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({"message": "링크가 유효하지 않습니다."}, status=status.HTTP_401_UNAUTHORIZED)

            return Response({"uidb64": uidb64, "token": token}, status=status.HTTP_200_OK)

        except DjangoUnicodeDecodeError as identifier:
            return Response({"message": "링크가 유효하지 않습니다."}, status=status.HTTP_401_UNAUTHORIZED)


class NewPasswordView(APIView):
    def put(self, request):
        serializer = SetNewPasswordSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"message": "비밀번호 재설정 완료"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ObtainUserTokenView(APIView):
    def post(self, request):
        serializer = TokenSerializer(
            data=request.data, context={"request": request})
        if serializer.is_valid():
            user = authenticate(
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
            )
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
