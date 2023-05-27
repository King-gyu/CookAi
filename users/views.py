from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from users.serializers import UserSerializer, MyPageSerializer, MyTokenObtainPairSerializer, UserProfileSerializer
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from users.tokens import account_activation_token
import traceback
from django.shortcuts import redirect, render
from .models import User
from articles.models import Article

from django.core.mail import send_mail

#회원가입
class UserSignupView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "가입이 완료 되었습니다."}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message":f"${serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)

#로그인
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    

#팔로우
class FollowView(APIView):
    def post(self, request, user_id):
        you = get_object_or_404(User, pk=user_id)
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
            return Response({'mesage': '권한이 없습니다!'}, status=status.HTTP_403_FORBIDDEN)

# 내게시글
class MyPageView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, user_id):
        ''' 회원의 아티클 받아오기'''
        user = get_object_or_404(User, id=user_id)
        myarticle = Article.objects.filter(user_id=user.id)
        serial = MyPageSerializer(myarticle, many=True)
        return Response(data=serial.data, status=status.HTTP_200_OK)

#회원정보
class UserProfileView(APIView):
    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        serializer = UserProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)  
        


#회원정보 수정
    def put(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        print(user, type(user))
        print(request.user, type(request.user))
        if user == request.user:
            serializer = UserSerializer(user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "수정완료!"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "권한이 없습니다!"}, status=status.HTTP_403_FORBIDDEN)

#회원탈퇴 (비화성화)
    def delete(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        if user == request.user:
            user.is_active = False
            user.save()
            return Response({"message": "탈퇴 되었습니다"}, status=status.HTTP_200_OK)
        else:
            return Response({"message":"유저가 일치하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)

#로그아웃
class UserLogoutView(APIView):
    def post(self, request):
        response = Response({"message": "로그아웃 완료"}, status=status.HTTP_200_OK)
        response.delete_cookie("access")
        response.delete_cookie("refresh")
        return response
    

#이메일 인증
class UserActivate(APIView):
    permission_classes = [AllowAny]
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_object_or_404(User, pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user=None

        try:
            if user is not None and account_activation_token.check_token(user, token):
                user.is_active = True
                user.save()
                return redirect('users:success')
            else:
                return Response({"message":"만료된 토큰"}, status=status.HTTP_408_REQUEST_TIMEOUT)
        
        except Exception as e:
            print(traceback.format_exc())

def active_success(request):
    return render(request, "email_active.html")