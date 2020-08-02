from django.contrib import admin
from blog.models import Post, Tag, Comment
from django.utils.safestring import mark_safe

admin.site.register(Tag)


@admin.register(Post)
class FlatAdmin(admin.ModelAdmin):
    fields = ('title', 'slug', 'author', 'tags', 'text', 'image', 'image_preview', 'published_at', 'likes',)
    search_fields = ('title', 'slug', 'author__username',)
    list_display = ('title', 'slug', 'author', 'published_at',)
    list_filter = ('published_at', 'tags__title')
    raw_id_fields = ('author', 'likes', 'tags',)
    readonly_fields = ('image_preview',)
    date_hierarchy = 'published_at'
    list_per_page = 20

    def image_preview(self, obj):
        return mark_safe(f'<img src = "{obj.image.url}" height = "200">')


@admin.register(Comment)
class FlatAdmin(admin.ModelAdmin):
    search_fields = ('post__title', 'author__username', 'text',)
    list_display = ('author', 'post', 'published_at',)
    list_filter = ('published_at',)
    raw_id_fields = ('author', 'post',)
    date_hierarchy = 'published_at'
    list_per_page = 20
