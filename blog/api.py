from django.db.models import F, Prefetch, Q
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


@router.get(
    "/posts",
    response=list[PostListOut],
    summary="List all published posts",
    description="Retrieve a paginated list of all published blog posts, including their authors and tags.",  # noqa: E501
    tags=["Posts"]
)
@paginate
def list_posts(request):
    posts = (
        Post.objects.filter(is_published=True)
        .select_related("author")
        .prefetch_related("tags")
        .order_by("-created_at")
    )
    return posts


@router.get(
    "/posts/search",
    response=list[PostListOut],
    summary="Search published posts",
    description="Retrieve a paginated list of published blog posts matching the search query.",
    tags=["Posts"]
)
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


@router.get(
    "/posts/by-tag/{slug}",
    response=list[PostListOut],
    summary="List posts by tag",
    description="Retrieve a paginated list of published blog posts associated with a specific tag.",
    tags=["Posts"]
)
@paginate
def posts_by_tag(request, slug: str):
    posts = (
        Post.objects.filter(tags__slug=slug, is_published=True)
        .select_related("author")
        .prefetch_related("tags")
        .order_by("-created_at")
    )
    return posts


@router.get(
    "/posts/{post_id}",
    response=PostDetailOut,
    summary="Get post details",
    description="Retrieve detailed information about a specific post, including its comments.",
    tags=["Posts"]
)
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


@router.post(
    "/posts",
    response=PostCreateOut,
    summary="Create a new post",
    description="Create a new blog post with the provided details.",
    tags=["Posts"]
)
def create_post(request, payload: PostCreateIn):
    author = get_object_or_404(User, id=payload.author_id)
    post = Post.objects.create(
        author=author,
        title=payload.title,
        body=payload.body,
    )
    tags = Tag.objects.filter(slug__in=payload.tag_slugs)
    post.tags.set(tags)
    return {"id": post.id, "title": post.title}


@router.post(
    "/posts/{post_id}/comments",
    response=CommentCreateOut,
    summary="Create a new comment",
    description="Create a new comment for a specific post.",
    tags=["Posts"]
)
def create_comment(request, post_id: int, payload: CommentCreateIn):
    post = get_object_or_404(Post, id=post_id)
    author = get_object_or_404(User, id=payload.author_id)
    comment = Comment.objects.create(post=post, author=author, body=payload.body)
    return {"id": comment.id}


@router.get(
    "/users/find",
    response=UserDetailOut,
    summary="Find user by email",
    description="Retrieve detailed information about a user based on their email address.",
    tags=["Users"]
)
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


@router.get(
    "/users/{user_id}",
    response=UserDetailOut,
    summary="Get user details",
    description="Retrieve detailed information about a specific user.",
    tags=["Users"]
)
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
