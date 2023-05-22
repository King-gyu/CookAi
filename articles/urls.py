# 게시글 및 댓글 작성, 수정, 삭제, 상세보기, 목록보기에 대한 url을 정의

from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path('articles/', views.ArticleListCreateView.as_view()),
    path('articles/<int:pk>/', views.ArticleRetrieveUpdateDestroyView.as_view()),
    path('articles/<int:article_pk>/comments/', views.CommentListCreateView.as_view()),
    path('articles/<int:article_pk>/comments/<int:pk>/', views.CommentRetrieveUpdateDestroyView.as_view()),
    path('articles/list/', views.article_list),
]