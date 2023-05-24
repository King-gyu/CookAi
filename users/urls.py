from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from users import views

urlpatterns = [
    path("signup/", views.SignupView.as_view(), name="signup"),
    path("verify-email/b'<str:uidb64>'/<str:token>/", views.VerifyEmailView.as_view(), name='verify-email'),
    path("login/", views.CustomTokenObtainPairView.as_view(), name='login'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path("logout/", views.UserList.as_view(), name="user_list"),
    path("<int:user_id>/detail/", views.ProfileView.as_view(), name="user_detail"),
    path("<int:user_id>/update/", views.ProfileView.as_view(), name='user_update'),
    path("<int:user_id>/delete/", views.UserDeleteView.as_view(), name='user_delete'),
    path("<int:user_id>/follow/", views.FollowView.as_view(), name="follow_view"),
    path("password/find/", views.PasswordResetView.as_view(), name='password_reset'),
    path("password/change/", views.NewPasswordView.as_view(), name="pw_change"), 
    path("password/change/b'<str:uidb64>'/<str:token>/", views.PasswordTokenCheckView.as_view(), name="pw_change_confirm"),
    path("password/change/confirm/", views.NewPasswordView.as_view(), name="pw_change_confirm"), 
]
