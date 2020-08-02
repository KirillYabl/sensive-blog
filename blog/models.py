from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Count


class TagQuerySet(models.QuerySet):

    def popular(self):
        popular_tags = self.annotate(num_posts=Count('posts')).order_by('-num_posts')
        return popular_tags

    def fetch_with_posts_count(self):
        tags_ids = [tag.id for tag in self]
        tags_with_posts_count = Tag.objects.filter(id__in=tags_ids).annotate(posts_count=Count('posts'))
        ids_and_posts_count = tags_with_posts_count.values_list('id', 'posts_count')
        count_for_id = dict(ids_and_posts_count)
        for tag in self:
            tag.posts_count = count_for_id[tag.id]

        return self


class PostQuerySet(models.QuerySet):

    def popular(self):
        popular_posts = self.annotate(likes_count=Count('likes')).order_by('-likes_count')
        return popular_posts

    def fetch_with_comments_count(self):
        posts_ids = [post.id for post in self]
        posts_with_comments_count = Post.objects.filter(id__in=posts_ids).annotate(comments_count=Count('comments'))
        ids_and_comments_count = posts_with_comments_count.values_list('id', 'comments_count')
        count_for_id = dict(ids_and_comments_count)
        for post in self:
            post.num_comments = count_for_id[post.id]

        return self

    def fetch_with_tags_posts_count(self):
        tags_ids = []
        for post in self:
            tags_ids += [tag.id for tag in post.tags.all()]
        tags_with_posts_count = Tag.objects.filter(id__in=tags_ids).annotate(posts_count=Count('posts'))
        ids_and_posts_count = tags_with_posts_count.values_list('id', 'posts_count')
        count_for_id = dict(ids_and_posts_count)
        for post in self:
            for tag in post.tags.all():
                tag.posts_count = count_for_id[tag.id]

        return self


class Post(models.Model):
    title = models.CharField(verbose_name="Заголовок", max_length=200)
    text = models.TextField(verbose_name="Текст")
    slug = models.SlugField(verbose_name="Название в виде url", max_length=200)
    image = models.ImageField(verbose_name="Картинка")
    published_at = models.DateTimeField(verbose_name="Дата и время публикации")

    author = models.ForeignKey(
        verbose_name="Автор",
        to=User,
        on_delete=models.CASCADE,
        related_name='posts',
        limit_choices_to={'is_staff': True}
    )
    likes = models.ManyToManyField(verbose_name="Кто лайкнул", to=User, related_name="liked_posts", blank=True)
    tags = models.ManyToManyField(verbose_name="Теги", to="Tag", related_name="posts")

    objects = PostQuerySet.as_manager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', args={'slug': self.slug})

    class Meta:
        ordering = ['-published_at']
        verbose_name = 'пост'
        verbose_name_plural = 'посты'


class Tag(models.Model):
    title = models.CharField(verbose_name="Тег", max_length=20, unique=True)

    objects = TagQuerySet.as_manager()

    def __str__(self):
        return self.title

    def clean(self):
        self.title = self.title.lower()

    def get_absolute_url(self):
        return reverse('tag_filter', args={'tag_title': self.slug})

    class Meta:
        ordering = ["title"]
        verbose_name = 'тег'
        verbose_name_plural = 'теги'


class Comment(models.Model):
    post = models.ForeignKey(
        verbose_name="Пост, к которому написан",
        to=Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(verbose_name="Автор", to=User, on_delete=models.CASCADE, related_name='comments')

    text = models.TextField(verbose_name="Текст комментария")
    published_at = models.DateTimeField(verbose_name="Дата и время публикации")

    def __str__(self):
        return f"{self.author.username} under {self.post.title}"

    class Meta:
        ordering = ['published_at']
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'
