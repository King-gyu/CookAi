# 게시글 및 댓글 작성, 수정, 삭제, 상세보기, 목록보기에 대한 url을 정의

from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path('', views.ArticleCreateView.as_view(), name='article_create'),
    path('<int:pk>/update/', views.ArticleUpdateView.as_view(), name='article_update'),
    path('<int:pk>/delete/', views.ArticleDeleteView.as_view(), name='article_delete'),
    path('<int:pk>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('list/', views.ArticleListView.as_view(), name='article_list'),
    
    path('<int:pk>/comments/', views.CommentCreateView.as_view(), name='comment_create'),
    path('<int:pk>/comments/<int:comment_pk>/', views.CommentUpdateView.as_view(), name='comment_update'),
    path('<int:pk>/comments/<int:comment_pk>/delete/', views.CommentDeleteView.as_view(), name='comment_delete'),
    path('<int:pk>/comments/<int:comment_pk>/detail/', views.CommentDetailView.as_view(), name='comment_detail'),
    path('<int:pk>/comments/<int:comment_pk>/list/', views.CommentListView.as_view(), name='comment_list'),
    path('cookai/', views.CookaiView.as_view(), name='cookai-1'),

]
