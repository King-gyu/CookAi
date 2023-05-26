from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Article, Comment, ImagesUp
from .serializers import ArticleSerializer, CommentSerializer, ImagesSerializer
from pathlib import Path
# from api_key import get_secret
import torch
import requests
import json
import os

BASE_DIR = Path(__file__).resolve().parent.parent
secret_file = os.path.join(BASE_DIR,'api_key.json')

with open(secret_file) as f:
    secrets = json.loads(f.read())


def get_secret(setting, secrets=secrets):
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {} environment variable".format(setting)
        raise error_msg


class CookaiView(APIView):
    # @login_required(login_url='')
    def post(self, request):
        '''cookai 이미지 판별 ai'''
        # cookai-1 의 이미지 판별함
        myimage = ImagesSerializer(data=request.data)
        if myimage.is_valid():
            myimage.save()      # 이미지 저장
        
        print(request.data['imgfile'])
        img = ImagesUp.objects.get(imgfile=request.data['imgfile'])
        # img = ImagesUp.objects.get(imgfile='KakaoTalk_20230407_165736763.jpg')
        
        
        #  Model
        model = torch.hub.load('ultralytics/yolov5', 'custom',
                            'C:/Users/shqk1/Desktop/sp/a8/CookAi/articles/weights/best.pt')  # custom trained model

        
        im = img.imgfile.path

        # Inference
        results = model(im)
        img.imgfile.storage.delete(img.imgfile.path)
        img.delete()
        df = results.pandas().xyxy[0].head(1)  # im predictions (pandas)
        try :
            max_cof = max(df['confidence'])# confidence
            
            
            if max_cof < 0.85:
                return Response({"메시지": "not found"},status=status.HTTP_200_OK)
            
            # # 결과값
            result = str(*df['name'].values)
            
            sample_dict = {
                'egg' : '계란',
                'tofu' : '두부',
            }
            
            api_key = get_secret('API_KEY')
            igd = sample_dict[result]
            print(igd)

            response = requests.get(f'https://openapi.foodsafetykorea.go.kr/api/{api_key}/COOKRCP01/json/1/9/RCP_NM={igd}')
            data = json.loads(response.text)
        except Exception as e :
            return Response({'error': e.message}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data = data, status=status.HTTP_200_OK)

        
# 게시글 작성

class ArticleCreateView(APIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    
    @login_required(login_url='')
    def post(self, request, *args, **kwargs):
        return render(request, 'articles/article_create.html')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
# 게시글 수정
class ArticleUpdateView(APIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    
    @login_required(login_url='')
    def put(self, request, *args, **kwargs):
        article = self.get_object()
        if article.author == request.user:
            return self.update(request, *args, **kwargs)
        else:
            return Response(status=403)
        
    def patch(self, request, *args, **kwargs):
        article = self.get_object()
        if article.author == request.user:
            return self.partial_update(request, *args, **kwargs)
        else:
            return Response(status=403)
        
    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

# 게시글 삭제
class ArticleDeleteView(APIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    
    @login_required(login_url='')
    def delete(self, request, *args, **kwargs):
        article = self.get_object()
        if article.author == request.user:
            article.delete()
            return Response(status=204)
        else:
            return Response(status=403)
        
    def perform_destroy(self, instance):
        instance.delete()

# 게시글 상세조회
class ArticleDetailView(APIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    
    def get(self, request, *args, **kwargs):
        article = self.get_object()
        serializer = self.get_serializer(article)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        article = self.get_object()
        serializer = self.get_serializer(article)
        return Response(serializer.data)
    
    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = get_object_or_404(queryset, pk=self.kwargs['pk'])
        self.check_object_permissions(self.request, obj)
        return obj

# 게시글 목록조회
class ArticleListView(APIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def get_queryset(self):
        queryset = Article.objects.all()
        return queryset

# 댓글 작성
class CommentCreateView(APIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    
    @login_required(login_url='')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        article = get_object_or_404(Article, pk=self.kwargs['pk'])
        serializer.save(author=self.request.user, article=article)

# 댓글 수정
class CommentUpdateView(APIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    
    @login_required(login_url='')
    def put(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author == request.user:
            return self.update(request, *args, **kwargs)
        else:
            return Response(status=403)
        
    def patch(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author == request.user:
            return self.partial_update(request, *args, **kwargs)
        else:
            return Response(status=403)
        
    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

# 댓글 삭제
class CommentDeleteView(APIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    
    @login_required(login_url='')
    def delete(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author == request.user:
            comment.delete()
            return Response(status=204)
        else:
            return Response(status=403)
        
    def perform_destroy(self, instance):
        instance.delete()

# 댓글 상세조회
class CommentDetailView(APIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    
    def get(self, request, *args, **kwargs):
        comment = self.get_object()
        serializer = self.get_serializer(comment)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        comment = self.get_object()
        serializer = self.get_serializer(comment)
        return Response(serializer.data)
    
    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = get_object_or_404(queryset, pk=self.kwargs['pk'])
        self.check_object_permissions(self.request, obj)
        return obj

# 댓글 목록조회
class CommentListView(APIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def list(self, request, *args, **kwargs):
        article = get_object_or_404(Article, pk=self.kwargs['pk'])
        queryset = self.filter_queryset(article.comment_set.all())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def get_queryset(self):
        article = get_object_or_404(Article, pk=self.kwargs['pk'])
        queryset = article.comment_set.all()
        return queryset

# 게시글 좋아요
class ArticleLikeView(APIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    
    @login_required(login_url='')
    def post(self, request, *args, **kwargs):
        article = self.get_object()
        if article.like_users.filter(pk=request.user.pk).exists():
            article.like_users.remove(request.user)
        else:
            article.like_users.add(request.user)
        serializer = self.get_serializer(article)
        return Response(serializer.data)
    
    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = get_object_or_404(queryset, pk=self.kwargs['pk'])
        self.check_object_permissions(self.request, obj)
        return obj

# 댓글 좋아요
class CommentLikeView(APIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    
    @login_required(login_url='')
    def post(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.like_users.filter(pk=request.user.pk).exists():
            comment.like_users.remove(request.user)
        else:
            comment.like_users.add(request.user)
        serializer = self.get_serializer(comment)
        return Response(serializer.data)
    
    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = get_object_or_404(queryset, pk=self.kwargs['pk'])
        self.check_object_permissions(self.request, obj)
        return obj

# 게시글 신고

# 댓글 신고

# 게시글 검색

# 댓글 검색

# 게시글 필터

# 댓글 필터

# 게시글 정렬

# 댓글 정렬