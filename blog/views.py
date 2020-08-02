from django.shortcuts import render, get_object_or_404
from blog.models import Comment, Post, Tag
from django.db.models.query import Prefetch


def serialize_post(post):
    return {
        "title": post.title,
        "teaser_text": post.text[:200],
        "author": post.author.username,
        "comments_amount": post.num_comments,
        "image_url": post.image.url if post.image else None,
        "published_at": post.published_at,
        "slug": post.slug,
        "tags": [serialize_tag(tag) for tag in post.tags.all()],
        'first_tag_title': post.tags.first().title,
    }


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.posts_count,
    }


def index(request):
    posts = Post.objects.prefetch_related(Prefetch('tags', Tag.objects.all().fetch_with_posts_count()), 'author')

    most_popular_posts = posts.popular()[:5]
    most_popular_posts_ids = [post.id for post in most_popular_posts]

    most_fresh_posts = posts.order_by('-published_at')[:5]
    most_fresh_posts_ids = [post.id for post in most_fresh_posts]

    # get the number of comments and posts, both the most popular and the most fresh
    union_posts_ids = most_popular_posts_ids + most_fresh_posts_ids
    union_posts = posts.filter(id__in=union_posts_ids). \
        fetch_with_comments_count().fetch_with_tags_posts_count()

    most_popular_tags = Tag.objects.popular()[:5].fetch_with_posts_count()

    context = {
        'most_popular_posts': [serialize_post(post) for post in union_posts if post.id in most_popular_posts_ids],
        'page_posts': [serialize_post(post) for post in union_posts if post.id in most_fresh_posts_ids],
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    posts = Post.objects.prefetch_related(Prefetch('tags', Tag.objects.all().fetch_with_posts_count()), 'author')
    post = get_object_or_404(posts, slug=slug)
    comments = post.comments.prefetch_related('author').all()
    serialized_comments = []
    for comment in comments:
        serialized_comments.append({
            'text': comment.text,
            'published_at': comment.published_at,
            'author': comment.author.username,
        })

    likes_count = post.likes.count()

    related_tags = post.tags.all().fetch_with_posts_count()

    serialized_post = {
        "title": post.title,
        "text": post.text,
        "author": post.author.username,
        "comments": serialized_comments,
        "likes_amount": likes_count,
        "image_url": post.image.url if post.image else None,
        "published_at": post.published_at,
        "slug": post.slug,
        "tags": [serialize_tag(tag) for tag in related_tags],
    }

    most_popular_tags = Tag.objects.popular()[:5].fetch_with_posts_count()

    most_popular_posts = posts.popular()[:5]. \
        fetch_with_comments_count().fetch_with_tags_posts_count()

    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'most_popular_posts': [serialize_post(post) for post in most_popular_posts],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = get_object_or_404(Tag, title=tag_title)

    most_popular_tags = Tag.objects.popular()[:5].fetch_with_posts_count()

    posts = Post.objects.prefetch_related(Prefetch('tags', Tag.objects.all().fetch_with_posts_count()), 'author')
    most_popular_posts = posts.popular()[:5].\
        fetch_with_comments_count().fetch_with_tags_posts_count()

    # this doesn't work with related_name
    related_posts = posts.filter(tags=tag)[:20]. \
        fetch_with_comments_count().fetch_with_tags_posts_count()

    context = {
        "tag": tag.title,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        "posts": [serialize_post(post) for post in related_posts],
        'most_popular_posts': [serialize_post(post) for post in most_popular_posts],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})
