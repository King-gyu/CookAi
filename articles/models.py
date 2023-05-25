from django.db import models
from users.models import User

# 게시글 모델 (작성자, 제목, 내용, 이미지, 작성일, 수정일, 좋아요)
class Article(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=30)
    content = models.TextField()
    image = models.ImageField(upload_to='article/%Y/%m/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='like_articles', blank=True)

    def __str__(self):
        return self.title

# 댓글 모델 (작성자, 내용, 이미지, 작성일, 수정일, 좋아요)
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comment_set')
    content = models.TextField()
    image = models.ImageField(upload_to='comment/%Y/%m/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='like_comments')
    
    def __str__(self):
        return self.content