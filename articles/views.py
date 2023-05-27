from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from articles.models import Article, Comment, Tag, ImagesUp
from articles.serializers import ImagesSerializer, ArticleSerializer, ArticleCreateSerializer, ArticleListSerializer, CommentSerializer, CommentCreateSerializer, TagSerializer
from rest_framework import status
from pathlib import Path
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
class TagView(APIView):
    def get(self, request):
        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def post(self, request):
        serializer = TagSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.erros, status=status.HTTP_400_BAD_REQUEST)
        
class TagDetailView(APIView):
    def get_object(self, pk):
        try:
            return Tag.objects.get(pk=pk)
        except Tag.DoesNotExist:
            return None

    def get(self, request, tag_pk):
        tag = self.get_object(tag_pk)
        if tag is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = TagSerializer(tag)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, tag_pk):
        tag = self.get_object(tag_pk)
        if tag is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = TagSerializer(tag, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, tag_pk):
        tag = self.get_object(tag_pk)
        if tag is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        tag.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class TagCreateView(APIView):
    def post(self, request):
        serializer = TagSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.erros, status=status.HTTP_400_BAD_REQUEST)

class ArticleView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        articles = Article.objects.all()
        serializer = ArticleListSerializer(articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def get_serializer_context(self):
        context = {'request': self.request}
        if hasattr(self, 'request'):
            context.update({'request': self.request})
        return context
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]

    def post(self, request):
        serializer = ArticleCreateSerializer(data=request.data, context=self.get_serializer_context())
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ArticleDetailView(APIView):
    def get(self, request, article_pk):
        article = get_object_or_404(Article, pk=article_pk)
        serializer = ArticleSerializer(article)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, article_pk):
        article = get_object_or_404(Article, pk=article_pk)
        if request.user == article.user:
            serializer = ArticleCreateSerializer(article, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("권한이 없습니다.", status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, article_pk):
        article = get_object_or_404(Article, pk=article_pk)
        if request.user == article.user:
            article.delete()
            return Response("삭제되었습니다.", status=status.HTTP_204_NO_CONTENT)
        else:
            return Response("권한이 없습니다.", status=status.HTTP_403_FORBIDDEN)


class CommentView(APIView):
    def get(self, request, article_pk):
        article = Article.objects.get(pk=article_pk)
        comments = article.comment_set.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, article_pk):
        serializer = CommentCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, article_pk=article_pk)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentDetailView(APIView):
    def get(self, request, article_pk, comment_pk):
        comment = Comment.objects.get(pk=comment_pk)
        serializer = CommentSerializer(comment)
        return Response(serializer.data)

    def put(self, request, article_pk, comment_pk):
        comment = get_object_or_404(Comment, pk=comment_pk)
        if request.user == comment.user:
            serializer = CommentCreateSerializer(comment, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("권한이 없습니다.", status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, article_pk, comment_pk):
        comment = get_object_or_404(Comment, pk=comment_pk)
        if request.user == comment.user:
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response("권한이 없습니다.", status=status.HTTP_403_FORBIDDEN)


class LikeView(APIView):
    def post(self, request, article_pk):
        article = get_object_or_404(Article, pk=article_pk)
        if request.user in article.likes.all():
            article.likes.remove(request.user)
            return Response("좋아요 취소", status=status.HTTP_200_OK)
        else:
            article.likes.add(request.user)
            return Response("좋아요", status=status.HTTP_200_OK)
        
