from django.contrib import admin
from blog.models import Post, Tag, Comment

admin.site.register(Tag)


@admin.register(Post)
class FlatAdmin(admin.ModelAdmin):
    search_fields = ('title', 'slug', 'author__username',)
    list_display = ('title', 'slug', 'author', 'published_at',)
    list_filter = ('published_at', 'tags__title')
    raw_id_fields = ('author', 'likes', 'tags',)
    date_hierarchy = 'published_at'
    list_per_page = 20


@admin.register(Comment)
class FlatAdmin(admin.ModelAdmin):
    search_fields = ('post__title', 'author__username', 'text',)
    list_display = ('author', 'post', 'published_at',)
    list_filter = ('published_at',)
    raw_id_fields = ('author', 'post',)
    date_hierarchy = 'published_at'
    list_per_page = 20
