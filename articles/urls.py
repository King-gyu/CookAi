# 게시글 및 댓글 작성, 수정, 삭제, 상세보기, 목록보기에 대한 url을 정의

from django.urls import path
from . import views

urlpatterns = [
    path('tags/', views.TagView.as_view(), name='tag_view'),
    path('tags/<int:tag_pk>/', views.TagDetailView.as_view(), name='tag_detail_view'),
    path('create_tag/', views.TagCreateView.as_view(), name='tag_create_view'),
    
    path('', views.ArticleView.as_view(), name='article_view'),
    path('<int:article_pk>/', views.ArticleDetailView.as_view(), name='article_detail_view'),
    
    path('<int:article_pk>/comment/', views.CommentView.as_view(), name='comment_view'),
    path('<int:article_pk>/comment/<int:comment_pk>/', views.CommentDetailView.as_view(), name='comment_detail_view'),

    path('<int:article_pk>/like/', views.LikeView.as_view(), name='like_view'),
    path('cookai/', views.CookaiView.as_view(), name='cookai-1'),
]
