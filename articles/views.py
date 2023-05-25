from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from articles.models import Article, Comment
from articles.serializers import ArticleSerializer, CommentSerializer


class ArticleView(APIView):
    def get(self, request):
        articles = Article.objects.all()
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ArticleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)


class ArticleDetailView(APIView):
    def get(self, request, article_pk):
        article = Article.objects.get(pk=article_pk)
        serializer = ArticleSerializer(article)
        return Response(serializer.data)

    def put(self, request, article_pk):
        article = Article.objects.get(pk=article_pk)
        serializer = ArticleSerializer(article, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)

    def delete(self, request, article_pk):
        article = Article.objects.get(pk=article_pk)
        article.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentView(APIView):
    def get(self, request):
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)


class CommentDetailView(APIView):
    def get(self, request, comment_pk):
        comment = Comment.objects.get(pk=comment_pk)
        serializer = CommentSerializer(comment)
        return Response(serializer.data)

    def put(self, request, comment_pk):
        comment = Comment.objects.get(pk=comment_pk)
        serializer = CommentSerializer(comment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)

    def delete(self, request, comment_pk):
        comment = Comment.objects.get(pk=comment_pk)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LikeView(APIView):
    def post(self, request):
        pass
