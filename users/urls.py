from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from users import views
from django.urls import path
app_name = 'users'

urlpatterns = [
    #회원가입
    path("signup/", views.UserSignupView.as_view(), name="signup"),

    #이메일인증
    path("activate/<slug:uidb64>/<slug:token>/", views.UserActivate.as_view(), name="activate"),
    path("success/", views.active_success, name="success"),

    #로그인
    path("login/", views.CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    #토큰 재발행
    path("login/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # 로그아웃
    path("logout/", views.UserLogoutView.as_view(), name='logout'),

    # 마이페이지
    path('mypage/<int:user_id>/', views.MyPageView.as_view(), name="mypage"),
    path('mypage/<int:user_id>/', views.FollowView.as_view(), name="mypage"),
    path('profile/<int:user_id>/', views.UserProfileView.as_view(), name="profile"),

    #팔로우
    path('follow/<int:user_id>/', views.FollowView.as_view(), name='follow_view'),

]
