from django.contrib import admin
from articles.models import Article, Comment, Tag


class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'created_at', 'updated_at']
    search_fields = ['title', 'content', 'user__email']
    list_filter = ['created_at', 'updated_at', 'user__email']
    ordering = ['-updated_at', '-created_at']


class CommentAdmin(admin.ModelAdmin):
    list_display = ['content', 'user', 'article', 'created_at', 'updated_at']
    search_fields = ['content', 'user__email', 'article__title']
    list_filter = ['created_at', 'updated_at', 'user__email']
    ordering = ['-updated_at', '-created_at']


class TagAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


admin.site.register(Article, ArticleAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Tag, TagAdmin)
