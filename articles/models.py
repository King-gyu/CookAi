from django.db import models
from django.utils import timezone
from users.models import User

# 게시글 모델 (작성자, 제목, 내용, 작성일, 수정일)
class Article(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True) # 최초 작성 시간
    updated_at = models.DateTimeField(auto_now=True) # 수정 시간

    def __str__(self):
        return f'{self.pk}번째 글, {self.title}'

# 댓글 모델 (작성자, 내용, 작성일, 수정일)
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    content = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True) # 최초 작성 시간
    updated_at = models.DateTimeField(auto_now=True) # 수정 시간

    def __str__(self):
        return f'<Article({self.article_id}): Comment({self.pk})-{self.content}>'
    
class ImagesUp(models.Model):
    user = "jychoi1996@gmail.com"
    imgfile = models.ImageField(null=True, upload_to="", blank=True) # 이거 고쳐야함