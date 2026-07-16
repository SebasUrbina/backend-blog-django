from django.db.models import Count, F, Prefetch, Q
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from blog.models import Comment, Post, Tag, User
from blog.schemas import (
    CommentCreateIn,
    CommentCreateOut,
    PostCreateIn,
    PostCreateOut,
    PostDetailOut,
    PostListOut,
    UserDetailOut,
)

router = Router()


@router.get("/posts", response=list[PostListOut])
@paginate
def list_posts(request):
    posts = (
        Post.objects.filter(is_published=True)
        .select_related("author")
        .prefetch_related("tags")
        .order_by("-created_at")
    )
    return posts


@router.get("/posts/search", response=list[PostListOut])
@paginate
def search_posts(request, q: str):
    posts = (
        Post.objects.filter(
            Q(title__icontains=q) | Q(body__icontains=q),
            is_published=True,
        )
        .select_related("author")
        .prefetch_related("tags")
        .order_by("-created_at")
    )
    return posts


@router.get("/posts/by-tag/{slug}", response=list[PostListOut])
@paginate
def posts_by_tag(request, slug: str):
    posts = (
        Post.objects.filter(tags__slug=slug, is_published=True)
        .select_related("author")
        .prefetch_related("tags")
        .order_by("-created_at")
    )
    return posts


@router.get("/posts/{post_id}", response=PostDetailOut)
def get_post(request, post_id: int):
    post = get_object_or_404(
        Post.objects.select_related("author").prefetch_related(
            "tags",
            Prefetch(
                "comments",
                queryset=Comment.objects.select_related("author"),
            ),
        ),
        id=post_id,
    )
    Post.objects.filter(id=post_id).update(view_count=F("view_count") + 1)
    post.view_count += 1
    return post


@router.post("/posts", response=PostCreateOut)
def create_post(request, payload: PostCreateIn):
    author = get_object_or_404(User, id=payload.author_id)
    post = Post.objects.create(
        author=author,
        title=payload.title,
        body=payload.body,
    )
    for slug in payload.tag_slugs:
        tag = Tag.objects.get(slug=slug)
        post.tags.add(tag)
    return {"id": post.id, "title": post.title}


@router.post("/posts/{post_id}/comments", response=CommentCreateOut)
def create_comment(request, post_id: int, payload: CommentCreateIn):
    post = get_object_or_404(Post, id=post_id)
    author = get_object_or_404(User, id=payload.author_id)
    comment = Comment.objects.create(post=post, author=author, body=payload.body)
    return {"id": comment.id}


@router.get("/users/find", response=UserDetailOut)
def find_user_by_email(request, email: str):

    user = get_object_or_404(User, email=email)

    return UserDetailOut(
        id=user.id,
        username=user.username,
        display_name=user.display_name,
        email=user.email,
        bio=user.bio,
        post_count=user.posts.count(),
        comment_count=user.comments.count(),
    )


@router.get("/users/{user_id}", response=UserDetailOut)
def get_user(request, user_id: int):
    user = get_object_or_404(User, id=user_id)
    return UserDetailOut(
        id=user.id,
        username=user.username,
        display_name=user.display_name,
        email=user.email,
        bio=user.bio,
        post_count=user.posts.count(),
        comment_count=user.comments.count(),
    )
